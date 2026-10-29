"""Independent fresh M5 attacks and two actual console-process match.

Run from the activated project venv: python3 <this_file> --output <new_dir>.
Loopback automation is not a human or external-machine test.
"""
from collections import Counter
from contextlib import contextmanager
from datetime import datetime
import argparse
import json
from pathlib import Path
import queue
import re
import select
import signal
import socket
import struct
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from tests.fixtures import FLEET, FLEET_CELLS, MISSES
from tests.meilenstein_04.test_gui import Peer

PERFORMER = 'automatisierter Codex-Testlauf (Rolle 3)'


@contextmanager
def running_server(output, label):
    raw = (output / f'{label}_server.txt').open('x')
    process = subprocess.Popen([sys.executable, '-u', str(ROOT / 'src/server.py'), '--host', '127.0.0.1', '--port', '0', '--log-file', str(output / f'{label}_messages.jsonl')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    lines = queue.Queue()
    def read():
        for line in process.stdout:
            raw.write(line)
            raw.flush()
            lines.put(line)
    thread = threading.Thread(target=read)
    thread.start()
    try:
        deadline = time.monotonic() + 5
        port = None
        while time.monotonic() < deadline:
            line = lines.get(timeout=max(.01, deadline - time.monotonic()))
            match = re.search(r'Server wartet auf Port (\d+)', line)
            if match:
                port = int(match.group(1))
                break
        assert port, 'Server never announced a listening port'
        yield ('127.0.0.1', port)
    finally:
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
            try: process.wait(3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(3)
        thread.join(3)
        process.stdout.close()
        raw.close()
        assert not thread.is_alive()
        assert process.returncode == 0, f'Server exit {process.returncode}'


def attacks(output):
    trace = []
    sockets = []
    table = []
    with running_server(output, 'attacks') as address:
        def new(name):
            sock = socket.create_connection(address, timeout=3)
            sockets.append(sock)
            peer = Peer(sock)
            peer.name = name
            return peer
        def send(peer, message):
            trace.append(dict(direction='outgoing', client=peer.name, message=message))
            peer.send(message)
        def recv(peer, kind):
            message = peer.read(3)
            trace.append(dict(direction='incoming', client=peer.name, message=message))
            assert message['type'] == kind, message
            return message
        def snapshot(peer):
            send(peer, {'type': 'getState'})
            return recv(peer, 'state')
        def pair(a, b):
            send(a, {'type': 'join', 'player': a.name})
            assert recv(a, 'welcome')['slot'] == 'A'
            recv(a, 'waiting'); recv(a, 'state')
            send(b, {'type': 'join', 'player': b.name})
            assert recv(b, 'welcome')['slot'] == 'B'
            for peer in (a, b): recv(peer, 'gameStart'); recv(peer, 'state')
        def place(a, b):
            for peer, fleet in ((a, FLEET), (b, [{**s, 'start': f'A{i+6}'} for i, s in enumerate(FLEET)])):
                send(peer, {'type': 'place', 'ships': fleet})
                recv(peer, 'placeAck')
                recv(a, 'state'); recv(b, 'state')
        try:
            a, b = new('Alice'), new('Bob')
            pair(a, b)
            place(a, b)
            cases = [
                ('1', 'ungueltiges JSON', a, b'{"type":"shoot",\n', 'INVALID_JSON'),
                ('2', 'falsch typisiertes Feld', a, {'type': 'shoot', 'field': 17}, 'CELL_OUT_OF_BOUNDS'),
                ('3', 'Feld ausserhalb', a, {'type': 'shoot', 'field': 'K1'}, 'CELL_OUT_OF_BOUNDS'),
                ('4', 'Pflichtfeld fehlt', a, {'type': 'shoot'}, 'CELL_OUT_OF_BOUNDS'),
                ('5', 'unbekannter Typ', a, {'type': 'grantVictory', 'winner': 'A'}, 'UNKNOWN_TYPE'),
                ('6', 'ausser der Reihe', b, {'type': 'shoot', 'field': 'A1'}, 'NOT_YOUR_TURN'),
            ]
            for number, title, peer, request, code in cases:
                before = [snapshot(a), snapshot(b)]
                if isinstance(request, bytes):
                    trace.append(dict(direction='outgoing', client=peer.name, raw=request.decode()))
                    peer.sock.sendall(request)
                else: send(peer, request)
                reply = recv(peer, 'error')
                assert reply['code'] == code, reply
                other = b if peer is a else a
                assert not select.select([other.sock], [], [], .05)[0], 'Private rejection leaked to opponent'
                after = [snapshot(a), snapshot(b)]
                assert after == before, 'Rejected input changed state or turn'
                assert after[0]['turn'] == after[1]['turn'] == 'A'
                table.append(dict(id=number, case=title, timestamp=datetime.now().astimezone().isoformat(), performer=PERFORMER, result='PASS', observed=f'{code}; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich'))
            # Abort while an active player's shoot frame is incomplete: real TCP reset.
            a.sock.sendall(b'{"type":"shoot","field":')
            trace.append(dict(direction='outgoing', client=a.name, raw='incomplete shoot frame then TCP RST'))
            a.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
            a.sock.close()
            recv(b, 'opponentLeft')
            reset = recv(b, 'state')
            assert reset['phase'] == 'waiting' and reset['turn'] is None and not reset['ownShips'] and not reset['shotsAtOpponent']
            c = new('Carol')
            send(c, {'type': 'join', 'player': 'Carol'})
            assert recv(c, 'welcome')['slot'] == 'A'
            for peer in (b, c): recv(peer, 'gameStart'); recv(peer, 'state')
            place(c, b)
            send(c, {'type': 'shoot', 'field': 'A6'})
            assert recv(c, 'result')['result'] == 'hit'
            for peer in (c, b): assert recv(peer, 'state')['turn'] == 'B'
            table.append(dict(id='7', case='Verbindung mitten im Zug trennen', timestamp=datetime.now().astimezone().isoformat(), performer=PERFORMER, result='PASS', observed='Unvollstaendiges shoot-JSON, TCP RST; Gegner informiert, leerer Reset, Ersatzbeitritt und naechster gueltiger Schuss erfolgreich'))
        finally:
            for sock in sockets:
                try: sock.shutdown(socket.SHUT_RDWR)
                except OSError: pass
                sock.close()
    (output / 'attack_client_messages.jsonl').write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in trace))
    (output / 'seven_attacks.json').write_text(json.dumps(table, ensure_ascii=False, indent=2) + '\n')
    lines = ['# Sieben Pflichtangriffe — frischer lokaler Lauf', '', f'Durchfuehrung: {PERFORMER}. Reale TCP-Sockets, alle Adressen Loopback; kein Fremdrechner-/Personennachweis.', '', '| Fall | Datum/Zeit | Beobachtung | Ergebnis |', '|---|---|---|---|']
    lines += [f"| {row['id']}: {row['case']} | {row['timestamp']} | {row['observed']} | {row['result']} |" for row in table]
    (output / 'seven_attacks.md').write_text('\n'.join(lines) + '\n')
    return table


class Console:
    def __init__(self, address, name, output):
        self.file = (output / f'console_{name}.txt').open('x')
        self.lines = queue.Queue()
        self.process = subprocess.Popen([sys.executable, '-u', str(ROOT / 'src/play.py'), address[0], name, '--port', str(address[1])], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        self.thread = threading.Thread(target=self.read)
        self.thread.start()
    def read(self):
        for line in self.process.stdout:
            self.file.write(line); self.file.flush(); self.lines.put(line.rstrip())
    def wait(self, predicate):
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            line = self.lines.get(timeout=max(.01, deadline-time.monotonic()))
            if predicate(line): return line
        raise AssertionError('Expected console line unavailable')
    def text(self, text): return self.wait(lambda line: text in line)
    def command(self, value): self.process.stdin.write(value + '\n'); self.process.stdin.flush()
    def close(self):
        if self.process.poll() is None:
            self.command('q')
            try: self.process.wait(3)
            except subprocess.TimeoutExpired: self.process.kill(); self.process.wait(3)
        self.thread.join(3)
        self.process.stdin.close(); self.process.stdout.close(); self.file.close()
        assert self.process.returncode == 0


def console_match(output):
    shots = []
    with running_server(output, 'console') as address:
        a = Console(address, 'Alice', output)
        b = None
        try:
            a.text('Du bist Spieler A')
            a.text('Warte auf Gegner')
            b = Console(address, 'Bob', output)
            b.text('Du bist Spieler B')
            for client in (a, b): client.text('Zustand -> Phase: shooting')
            b.command('J1')
            b.text('NOT_YOUR_TURN')
            for index, field in enumerate(FLEET_CELLS):
                a.command(field)
                result = a.text(f'Schuss auf {field}:')
                shots.append(dict(player='A', field=field, line=result))
                if index == 16:
                    assert 'Gewonnen!' in result
                    b.text('Spiel beendet. Gewinner: A')
                    for client in (a, b): client.text('Zustand -> Phase: finished')
                else:
                    for client in (a, b): client.text('am Zug: B')
                    miss = MISSES[index]
                    b.command(miss)
                    result = b.text(f'Schuss auf {miss}: miss')
                    shots.append(dict(player='B', field=miss, line=result))
                    for client in (a, b): client.text('am Zug: A')
            assert len(shots) == 33
        finally:
            if b: b.close()
            a.close()
    report = dict(timestamp=datetime.now().astimezone().isoformat(), performer=PERFORMER, result='PASS', scope='Serverprozess und zwei echte play.py-Prozesse lokal ueber TCP', shots=shots, checks=['Warten/Beitritt', 'automatische Standardflotte', 'NOT_YOUR_TURN', '33 gueltige Schuesse', 'Sieg A/Niederlage B', 'sauberes Clientende'])
    (output / 'console_result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


def check_persistent_logs(output):
    counts = {}
    for label in ('attacks', 'console'):
        path = output / f'{label}_messages.jsonl'
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        assert rows
        for row in rows:
            assert datetime.fromisoformat(row['timestamp']).utcoffset() is not None
            assert row['direction'] in ('<-', '->')
            assert set(row) <= {'timestamp', 'direction', 'peer', 'slot', 'type', 'code'}
        text = path.read_text()
        assert not any(secret in text for secret in ('ownShips', 'shotsAtOpponent', 'Carrier', 'Alice', 'grantVictory'))
        counts[label] = dict(Counter(row['direction'] for row in rows))
    server_text = ''.join((output / f'{label}_server.txt').read_text() for label in ('attacks', 'console'))
    assert 'Traceback' not in server_text
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    report = dict(started_at=datetime.now().astimezone().isoformat(), performer=PERFORMER, result='FAIL')
    try:
        report['attacks'] = len(attacks(args.output))
        report['console_shots'] = len(console_match(args.output)['shots'])
        report['persistent_log_counts'] = check_persistent_logs(args.output)
        report['result'] = 'PASS'
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        report['finished_at'] = datetime.now().astimezone().isoformat()
        (args.output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()

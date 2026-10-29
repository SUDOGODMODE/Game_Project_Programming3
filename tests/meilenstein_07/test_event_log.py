"""Persistent metadata for actual messages; no untrusted text or private payloads."""
from collections import Counter
from datetime import datetime
import importlib
import json
from pathlib import Path
import socket
import tempfile
import threading
import unittest

import server
from netz import send
from tests.meilenstein_04.test_gui import Peer


class EventLogTests(unittest.TestCase):
    def event_log(self, path):
        spec = importlib.util.find_spec('event_log')
        self.assertIsNotNone(spec, 'Persistent EventLog is missing')
        return importlib.import_module('event_log').EventLog(path)

    def entries(self, path):
        lines = path.read_text().splitlines()
        rows = [json.loads(line) for line in lines]
        for row in rows:
            stamp = datetime.fromisoformat(row['timestamp'])
            self.assertIsNotNone(stamp.utcoffset(), 'Timestamp must identify timezone')
            self.assertIn(row['direction'], ('<-', '->'))
            self.assertIsInstance(row['peer'], str)
            self.assertIn('slot', row)
        return rows

    def test_metadata_is_immediately_persistent_and_excludes_client_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'new.jsonl'
            log = self.event_log(path)
            self.addCleanup(log.close)
            log.record('<-', 'peer-1', {'type': 'place', 'ships': [{'SECRET_FLEET': 'Q9'}], 'player': 'SECRET_PLAYER'}, slot='A')
            log.record('<-', 'peer-1', {'type': 'EVIL_TYPE\nINJECTION', 'code': 'SECRET_CODE'}, slot='A')
            log.record('->', 'peer-1', {'type': 'error', 'code': 'NOT_YOUR_TURN', 'message': 'SECRET_ERROR'}, slot='A')
            rows = self.entries(path)  # before close: each accepted message must already persist
            self.assertEqual([r['type'] for r in rows], ['place', 'unknown', 'error'])
            self.assertEqual(rows[-1]['code'], 'NOT_YOUR_TURN')
            self.assertNotIn('code', rows[1])
            self.assertNotIn('SECRET', path.read_text())
            self.assertNotIn('EVIL', path.read_text())
            self.assertEqual(rows[0]['slot'], 'A')

    def test_parallel_messages_form_complete_independent_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'parallel.jsonl'
            log = self.event_log(path)
            self.addCleanup(log.close)
            errors = []
            def write(peer):
                try:
                    for _ in range(40): log.record('<-', peer, {'type': 'getState'})
                except Exception as exc: errors.append(exc)
            threads = [threading.Thread(target=write, args=(f'peer-{i}',)) for i in range(6)]
            for thread in threads: thread.start()
            for thread in threads: thread.join(3)
            self.assertFalse(any(t.is_alive() for t in threads))
            self.assertEqual(errors, [])
            rows = self.entries(path)
            self.assertEqual(Counter(r['peer'] for r in rows), {f'peer-{i}': 40 for i in range(6)})

    def test_existing_file_cannot_be_truncated_or_appended(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'old.jsonl'
            path.write_bytes(b'old immutable evidence\n')
            with self.assertRaises(FileExistsError): self.event_log(path)
            self.assertEqual(path.read_bytes(), b'old immutable evidence\n')

    def test_actual_handler_logs_each_received_and_sent_message_through_abort(self):
        self.assertIn('log_file', __import__('inspect').signature(server.new_game).parameters, 'new_game must own a persistent log')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'wire.jsonl'
            game = server.new_game(log_file=path)
            errors = []
            local, remote = socket.socketpair()
            def serve():
                try: server.handle_connection(local, ('127.0.0.1', 12345), game)
                except Exception as exc: errors.append(exc)
            worker = threading.Thread(target=serve)
            worker.start()
            peer = Peer(remote)
            received = []
            try:
                send(remote, {'type': 'join', 'player': 'PRIVATE_NAME'})
                for _ in range(3): received.append(peer.read())
                remote.sendall(b'{not JSON}\n')
                received.append(peer.read())
                send(remote, {'type': 'getState'})
                received.append(peer.read())
            finally:
                remote.shutdown(socket.SHUT_RDWR)
                remote.close()
                worker.join(3)
                game['event_log'].close()
            self.assertFalse(worker.is_alive())
            self.assertEqual(errors, [])
            rows = self.entries(path)
            self.assertEqual([r['type'] for r in rows if r['direction'] == '<-'], ['join', 'broken', 'getState'])
            self.assertEqual([r['type'] for r in rows if r['direction'] == '->'], [m['type'] for m in received])
            self.assertEqual(len(rows), 8)
            self.assertNotIn('PRIVATE_NAME', path.read_text())
            self.assertNotIn('ownShips', path.read_text())

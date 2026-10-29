"""Tests für JSON-Zeilen: python tools/run_tests.py --milestone 03."""
import json
import io
import queue
import socket
import threading
import unittest

from netz import read_messages, send


class TestTransport(unittest.TestCase):
    def setUp(self):
        self.sender, self.receiver = socket.socketpair()
        self.messages = read_messages(self.receiver)

    def tearDown(self):
        self.sender.close()
        self.messages.close()
        self.receiver.close()

    def test_send_preserves_unicode_and_escapes_newlines(self):
        send(self.sender, {"type": "join", "player": "Jörg\nMüller"})
        raw = self.receiver.recv(1024)
        self.assertEqual(raw.count(b"\n"), 1)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertIn("Jörg".encode("utf-8"), raw)
        self.assertEqual(json.loads(raw), {"type": "join", "player": "Jörg\nMüller"})

    def test_two_messages_in_one_send_are_read_separately(self):
        self.sender.sendall(b'{"type":"join","player":"Alice"}\n{"type":"getState"}\n')
        self.assertEqual(next(self.messages), {"type": "join", "player": "Alice"})
        self.assertEqual(next(self.messages), {"type": "getState"})

    def test_fragmented_utf8_message_waits_for_its_complete_line(self):
        raw = '{"type":"join","player":"Jörg"}\n'.encode("utf-8")
        split = raw.index("ö".encode("utf-8")) + 1
        received = queue.Queue()

        def read_one():
            try:
                received.put(next(self.messages))
            except Exception as exc:
                received.put(exc)

        reader = threading.Thread(target=read_one, daemon=True)
        reader.start()
        try:
            self.sender.sendall(raw[:split])
            with self.assertRaises(queue.Empty):
                received.get(timeout=0.05)
            self.sender.sendall(raw[split:])
            self.assertEqual(received.get(timeout=2), {"type": "join", "player": "Jörg"})
        finally:
            self.sender.shutdown(socket.SHUT_WR)
            reader.join(timeout=2)
        self.assertFalse(reader.is_alive())

    def test_invalid_json_and_non_objects_do_not_lose_the_next_message(self):
        self.sender.sendall(b'kein json\n[1,2]\nnull\n42\n{"type":"getState"}\n')
        for _ in range(4):
            self.assertEqual(next(self.messages), {"type": "broken"})
        self.assertEqual(next(self.messages), {"type": "getState"})

    def test_empty_lines_are_ignored_and_eof_ends_the_reader(self):
        self.sender.sendall(b'\n \n{"type":"getState"}\n')
        self.sender.shutdown(socket.SHUT_WR)
        self.assertEqual(next(self.messages), {"type": "getState"})
        with self.assertRaises(StopIteration):
            next(self.messages)

    def test_hard_read_error_ends_reader_and_closes_stream(self):
        class BrokenStream(io.StringIO):
            def __next__(self):
                raise ConnectionResetError("connection reset")

        class Connection:
            def makefile(self, *args, **kwargs):
                return stream

        stream = BrokenStream()
        try:
            messages = list(read_messages(Connection()))
        except OSError as error:
            self.fail(f"Ein harter Leseabbruch muss den Leser normal beenden: {error}")
        self.assertEqual(messages, [])
        self.assertTrue(stream.closed, "Der Netzwerkleser muss seinen Textstream schliessen")


if __name__ == "__main__":
    unittest.main()

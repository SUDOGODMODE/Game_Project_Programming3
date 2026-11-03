"""Startet Schiffe versenken mit festen Adressregeln je Betriebsprofil."""

import argparse
from ipaddress import AddressValueError, IPv4Address
from pathlib import Path
import subprocess
import sys


PROFILES = ("localhost", "zwei_rechner")
ROLES = ("server", "alice", "bob")
ROOT = Path(__file__).resolve().parents[1]


def _server_ipv4(value: str | None) -> str:
    """Prueft Bobs ausdruecklich angegebene Zieladresse vor dem Start."""
    if not isinstance(value, str) or not value:
        raise ValueError("Bob braucht --server-ip mit der IPv4-Adresse von Rechner 1")
    try:
        address = IPv4Address(value)
    except AddressValueError as exc:
        raise ValueError("--server-ip muss eine gueltige IPv4-Adresse sein") from exc
    if (address.is_loopback or address.is_unspecified or address.is_multicast
            or address.is_reserved or address.is_link_local):
        raise ValueError("--server-ip muss eine erreichbare IPv4-Hostadresse von Rechner 1 sein")
    return str(address)


def command_for(profile: str, role: str, *, server_ip: str | None = None,
                port: int = 5100, name: str | None = None,
                root: Path, python: str) -> list[str]:
    """Baut einen Prozessaufruf ohne Shell oder geerbte Netzwerk-Defaults."""
    if profile not in PROFILES:
        raise ValueError(f"unbekanntes Startprofil: {profile}")
    if role not in ROLES:
        raise ValueError(f"unbekannte Rolle: {role}")
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("--port muss eine Zahl zwischen 1 und 65535 sein")
    if role != "bob" or profile == "localhost":
        if server_ip is not None:
            raise ValueError("--server-ip ist nur fuer Bob im Zwei-Rechner-Profil zulaessig")

    root = Path(root).absolute()
    if role == "server":
        if name is not None:
            raise ValueError("--name ist nur fuer Clients zulaessig")
        host = "127.0.0.1" if profile == "localhost" else "0.0.0.0"
        return [python, "-u", str(root / "src/server.py"), "--host", host,
                "--port", str(port)]

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Alice und Bob brauchen einen nichtleeren --name")
    host = _server_ipv4(server_ip) if profile == "zwei_rechner" and role == "bob" else "127.0.0.1"
    return [python, str(root / "src/client_gui.py"), host, name, "--port", str(port)]


def main(profile: str, argv: list[str] | None = None) -> int:
    """Parst eine Rolle und startet genau einen Prozess des gewaehlten Profils."""
    parser = argparse.ArgumentParser(description=f"Schiffe versenken: {profile}")
    parser.add_argument("role", choices=ROLES, help="server, alice oder bob")
    parser.add_argument("--name", help="Spielername fuer alice oder bob")
    parser.add_argument("--server-ip", help="IPv4-Adresse von Rechner 1 fuer bob im Zwei-Rechner-Profil")
    parser.add_argument("--port", type=int, default=5100, help="gleicher TCP-Port auf allen Geraeten (Standard: 5100)")
    args = parser.parse_args(argv)
    try:
        command = command_for(profile, args.role, server_ip=args.server_ip,
                              port=args.port, name=args.name, root=ROOT,
                              python=sys.executable)
    except ValueError as exc:
        parser.error(str(exc))
    try:
        return subprocess.run(command, check=False).returncode
    except KeyboardInterrupt:
        return 130

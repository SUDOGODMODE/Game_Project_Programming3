# Spec Kit: Recherche und lokale Einführung vom 10.11.2026

Die am 07.11. unterbrochene Recherche wurde abgeschlossen. Anschließend
stellte der Projektverantwortliche klar, dass Spec Kit tatsächlich installiert
und genutzt werden soll. `specify-cli` **1.3.3** wurde mit `uv tool install`
vom offiziellen Tag installiert und dieses bestehende Repository mit
`--integration codex --script sh` initialisiert. `specify --version` meldet
1.3.3; `specify check` erkennt Codex CLI. Die Projektgrundsätze wurden mit
`$speckit-constitution` in `.specify/memory/constitution.md` erfasst.

Das offizielle Release [v1.3.3](https://github.com/github/spec-kit/releases/tag/v1.3.3)
vom 09.11.2026 nutzt für Codex `--integration codex`. Die
[Installationsanleitung](https://github.com/github/spec-kit/blob/main/docs/installation.md)
beschreibt `specify-cli` und Python ab 3.11. Der Kern legt Projektdateien
unter `.specify/` und Codex-Skills unter `.agents/skills/speckit-*/` ab.
Neue Spezifikationen liegen üblicherweise unter `specs/`; vorhandene
`docs/superpowers/specs/` und `docs/superpowers/plans/` müssen dafür nicht
verschoben werden. Siehe [Codex-Integration](https://github.com/github/spec-kit/blob/main/docs/integrations/codex.md)
und [Bestandsprojekte](https://github.com/github/spec-kit/blob/main/docs/how-to/existing-projects.md).

Installiert wurde im vorhandenen lokalen Feature-Branch, ohne Commit oder
Push. Die optionalen Erweiterungen
für [Git](https://github.com/github/spec-kit/blob/main/extensions/git/README.md)
und [Agent-Kontext](https://github.com/github/spec-kit/blob/main/extensions/agent-context/README.md)
wurden nicht hinzugefügt. Die vorhandenen Spezifikationen unter
`docs/superpowers/` bleiben erhalten. Neue Aufgaben können mit den Codex-Skills
`$speckit-specify`, `$speckit-plan` und `$speckit-tasks` bearbeitet werden.
Das Abgabewerkzeug schließt `.specify/` und `.agents/` aus einem Spiel-ZIP
aus. Ein rot/grün geprüfter Pakettest und ein echtes temporäres Archiv
bestätigen den Ausschluss.

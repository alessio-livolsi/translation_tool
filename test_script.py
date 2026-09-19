from unittest.mock import Mock

import pytest

import script


@pytest.fixture
def mock_po_file():
    """Return a mocked PO file containing representative entries."""
    empty_msgid = Mock(msgid="", msgstr="")
    untranslated = Mock(msgid="Hello", msgstr="")
    already_translated = Mock(msgid="Goodbye", msgstr="Au revoir")

    po_file = Mock()
    po_file.__iter__ = Mock(
        return_value=iter(
            [
                empty_msgid,
                untranslated,
                already_translated,
            ]
        )
    )

    return po_file, untranslated


def test_main_exits_when_filename_is_empty(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "")

    with pytest.raises(SystemExit) as exc_info:
        script.main()

    assert exc_info.value.code == 1
    assert "Error: no filename was entered." in capsys.readouterr().out


def test_main_exits_when_source_file_does_not_exist(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "missing.po")
    monkeypatch.setattr(script.os.path, "isfile", lambda _: False)

    with pytest.raises(SystemExit) as exc_info:
        script.main()

    assert exc_info.value.code == 1
    assert "Error: 'missing.po' does not exist." in capsys.readouterr().out


def test_main_exits_for_unknown_language(monkeypatch, capsys):
    answers = iter(["messages.po", "not-a-language"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)

    with pytest.raises(SystemExit) as exc_info:
        script.main()

    assert exc_info.value.code == 1

    output = capsys.readouterr().out
    assert "Error: unknown language code 'not-a-language'." in output


def test_main_normalizes_destination_language(monkeypatch, mock_po_file):
    po_file, untranslated = mock_po_file
    answers = iter(["messages.po", " FR "])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(script.polib, "pofile", lambda _: po_file)
    monkeypatch.setattr(script, "tqdm", lambda iterable, **_: iterable)

    translator = Mock()
    translator.translate.return_value.text = "Bonjour"
    monkeypatch.setattr(script, "Translator", lambda: translator)

    script.main()

    translator.translate.assert_called_once_with(
        "Hello",
        dest="fr",
    )
    assert untranslated.msgstr == "Bonjour"


@pytest.mark.parametrize(
    "error",
    [
        OSError("cannot read file"),
        UnicodeError("invalid encoding"),
    ],
)
def test_main_exits_when_po_file_cannot_be_loaded(
    monkeypatch,
    capsys,
    error,
):
    answers = iter(["messages.po", "fr"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)

    def raise_error(_):
        raise error

    monkeypatch.setattr(script.polib, "pofile", raise_error)

    with pytest.raises(SystemExit) as exc_info:
        script.main()

    assert exc_info.value.code == 1
    assert "Error: unable to load 'messages.po'" in capsys.readouterr().out


def test_main_translates_untranslated_entries(
    monkeypatch,
    mock_po_file,
):
    po_file, untranslated = mock_po_file
    answers = iter(["messages.po", "fr"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(script.polib, "pofile", lambda _: po_file)
    monkeypatch.setattr(script, "tqdm", lambda iterable, **_: iterable)

    translator = Mock()
    translator.translate.return_value.text = "Bonjour"
    monkeypatch.setattr(script, "Translator", lambda: translator)

    script.main()

    assert untranslated.msgstr == "Bonjour"
    translator.translate.assert_called_once_with(
        "Hello",
        dest="fr",
    )


def test_main_skips_entries_with_existing_translation(monkeypatch):
    translated_entry = Mock(
        msgid="Hello",
        msgstr="Bonjour",
    )

    po_file = Mock()
    po_file.__iter__ = Mock(return_value=iter([translated_entry]))

    answers = iter(["messages.po", "fr"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(script.polib, "pofile", lambda _: po_file)
    monkeypatch.setattr(script, "tqdm", lambda iterable, **_: iterable)

    translator = Mock()
    monkeypatch.setattr(script, "Translator", lambda: translator)

    script.main()

    translator.translate.assert_not_called()
    assert translated_entry.msgstr == "Bonjour"


def test_main_skips_entries_with_empty_msgid(monkeypatch):
    empty_entry = Mock(msgid="", msgstr="")

    po_file = Mock()
    po_file.__iter__ = Mock(return_value=iter([empty_entry]))

    answers = iter(["messages.po", "fr"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(script.polib, "pofile", lambda _: po_file)
    monkeypatch.setattr(script, "tqdm", lambda iterable, **_: iterable)

    translator = Mock()
    monkeypatch.setattr(script, "Translator", lambda: translator)

    script.main()

    translator.translate.assert_not_called()


def test_main_continues_when_translation_fails(monkeypatch):
    failed_entry = Mock(msgid="Hello", msgstr="")
    successful_entry = Mock(msgid="Goodbye", msgstr="")

    po_file = Mock()
    po_file.__iter__ = Mock(return_value=iter([failed_entry, successful_entry]))

    answers = iter(["messages.po", "fr"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(script.polib, "pofile", lambda _: po_file)
    monkeypatch.setattr(script, "tqdm", lambda iterable, **_: iterable)

    translator = Mock()
    translator.translate.side_effect = [
        Exception("translation service unavailable"),
        Mock(text="Au revoir"),
    ]
    monkeypatch.setattr(script, "Translator", lambda: translator)

    script.main()

    assert failed_entry.msgstr == ""
    assert successful_entry.msgstr == "Au revoir"
    assert translator.translate.call_count == 2


def test_main_creates_output_directory(monkeypatch, mock_po_file):
    po_file, _ = mock_po_file
    answers = iter(["messages.po", "fr"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(script.polib, "pofile", lambda _: po_file)
    monkeypatch.setattr(script, "tqdm", lambda iterable, **_: iterable)

    translator = Mock()
    translator.translate.return_value.text = "Bonjour"
    monkeypatch.setattr(script, "Translator", lambda: translator)

    makedirs = Mock()
    monkeypatch.setattr(script.os, "makedirs", makedirs)

    script.main()

    makedirs.assert_called_once_with(
        script.OUTPUT_DIRECTORY,
        exist_ok=True,
    )


def test_main_saves_translated_po_file(monkeypatch, mock_po_file):
    po_file, _ = mock_po_file
    answers = iter(["some/path/messages.po", "fr"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(script.polib, "pofile", lambda _: po_file)
    monkeypatch.setattr(script, "tqdm", lambda iterable, **_: iterable)

    translator = Mock()
    translator.translate.return_value.text = "Bonjour"
    monkeypatch.setattr(script, "Translator", lambda: translator)

    script.main()

    expected_filename = script.os.path.join(
        script.OUTPUT_DIRECTORY,
        "messages_fr.po",
    )

    po_file.save.assert_called_once_with(expected_filename)


def test_main_exits_when_po_file_cannot_be_saved(
    monkeypatch,
    mock_po_file,
    capsys,
):
    po_file, _ = mock_po_file
    po_file.save.side_effect = OSError("permission denied")

    answers = iter(["messages.po", "fr"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(script.polib, "pofile", lambda _: po_file)
    monkeypatch.setattr(script, "tqdm", lambda iterable, **_: iterable)

    translator = Mock()
    translator.translate.return_value.text = "Bonjour"
    monkeypatch.setattr(script, "Translator", lambda: translator)

    with pytest.raises(SystemExit) as exc_info:
        script.main()

    assert exc_info.value.code == 1
    assert "Error: unable to save" in capsys.readouterr().out


def test_main_prints_success_message(
    monkeypatch,
    mock_po_file,
    capsys,
):
    po_file, _ = mock_po_file
    answers = iter(["messages.po", "fr"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(script.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(script.polib, "pofile", lambda _: po_file)
    monkeypatch.setattr(script, "tqdm", lambda iterable, **_: iterable)

    translator = Mock()
    translator.translate.return_value.text = "Bonjour"
    monkeypatch.setattr(script, "Translator", lambda: translator)

    script.main()

    expected_filename = script.os.path.join(
        script.OUTPUT_DIRECTORY,
        "messages_fr.po",
    )

    assert (
        f"Your file has been translated and saved as "
        f"'{expected_filename}'." in capsys.readouterr().out
    )

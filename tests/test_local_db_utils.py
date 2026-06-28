import builtins
import pickle
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

from bot.utils.local_db_utils import load_local_db, save2db_lcl, save2db_lcl2


@pytest.fixture
def mock_bot():
    with patch("bot.utils.local_db_utils._bot") as mock_bot:
        mock_bot.queue = {}
        mock_bot.batch_queue = {}
        mock_bot.rss_dict = {}
        mock_bot.temp_users = []
        mock_bot.custom_rename = None
        yield mock_bot


@pytest.fixture
def mock_file_exists():
    with patch("bot.utils.local_db_utils.file_exists") as mock_file_exists:
        yield mock_file_exists


@pytest.fixture
def mock_pickle_load():
    with patch("bot.utils.local_db_utils.pickle.load") as mock_pickle_load:
        yield mock_pickle_load


@pytest.fixture
def mock_pickle_dump():
    with patch("bot.utils.local_db_utils.pickle.dump") as mock_pickle_dump:
        yield mock_pickle_dump


@pytest.fixture
def mock_list_to_str():
    with patch("bot.utils.local_db_utils.list_to_str") as mock_list_to_str:
        yield mock_list_to_str


@patch("bot.utils.local_db_utils.local_qdb", "local_qdb.pkl")
@patch("bot.utils.local_db_utils.local_qdb2", "local_qdb2.pkl")
@patch("bot.utils.local_db_utils.local_rdb", "local_rdb.pkl")
@patch("bot.utils.local_db_utils.local_udb", "local_udb.pkl")
@patch("bot.utils.local_db_utils.local_cdb", "local_cdb.pkl")
def test_load_local_db_all_exist(mock_bot, mock_file_exists, mock_pickle_load):
    mock_file_exists.return_value = True

    mock_pickle_load.side_effect = [
        {"q1": "data1"},
        {"bq1": "data2"},
        {"rss1": "data3"},
        "user1 user2 user3",
        "format1",
    ]

    with patch("builtins.open", mock_open()) as mock_file:
        load_local_db()

        assert mock_bot.queue == {"q1": "data1"}
        assert mock_bot.batch_queue == {"bq1": "data2"}
        assert mock_bot.rss_dict == {"rss1": "data3"}
        assert mock_bot.temp_users == ["user1", "user2", "user3"]
        assert mock_bot.custom_rename == "format1"

        assert mock_file.call_count == 5
        mock_file.assert_has_calls([
            call("local_qdb.pkl", "rb"),
            call("local_qdb2.pkl", "rb"),
            call("local_rdb.pkl", "rb"),
            call("local_udb.pkl", "rb"),
            call("local_cdb.pkl", "rb"),
        ], any_order=True)


@patch("bot.utils.local_db_utils.local_qdb", "local_qdb.pkl")
@patch("bot.utils.local_db_utils.local_qdb2", "local_qdb2.pkl")
@patch("bot.utils.local_db_utils.local_rdb", "local_rdb.pkl")
@patch("bot.utils.local_db_utils.local_udb", "local_udb.pkl")
@patch("bot.utils.local_db_utils.local_cdb", "local_cdb.pkl")
def test_load_local_db_none_exist(mock_bot, mock_file_exists, mock_pickle_load):
    mock_file_exists.return_value = False

    with patch("builtins.open", mock_open()) as mock_file:
        load_local_db()

        assert mock_bot.queue == {}
        assert mock_bot.batch_queue == {}
        assert mock_bot.rss_dict == {}
        assert mock_bot.temp_users == []
        assert mock_bot.custom_rename is None

        mock_file.assert_not_called()
        mock_pickle_load.assert_not_called()


@patch("bot.utils.local_db_utils.local_udb", "local_udb.pkl")
def test_load_local_db_duplicate_users(mock_bot, mock_file_exists, mock_pickle_load):
    mock_file_exists.side_effect = lambda f: f == "local_udb.pkl"
    mock_pickle_load.return_value = "user1 user2 user1"
    mock_bot.temp_users = ["user3"]

    with patch("builtins.open", mock_open()):
        load_local_db()

        assert mock_bot.temp_users == ["user3", "user1", "user2"]


@patch("bot.utils.local_db_utils.local_qdb", "local_qdb.pkl")
@patch("bot.utils.local_db_utils.local_qdb2", "local_qdb2.pkl")
def test_save2db_lcl(mock_bot, mock_pickle_dump):
    mock_bot.queue = {"q1": "data1"}
    mock_bot.batch_queue = {"bq1": "data2"}

    with patch("builtins.open", mock_open()) as mock_file:
        save2db_lcl()

        assert mock_file.call_count == 2
        mock_file.assert_has_calls([
            call("local_qdb.pkl", "wb"),
            call("local_qdb2.pkl", "wb"),
        ], any_order=True)

        assert mock_pickle_dump.call_count == 2
        # Verify the calls somehow. mock_pickle_dump is called with the object and the file handle
        dump_args = [args[0] for args, kwargs in mock_pickle_dump.call_args_list]
        assert {"q1": "data1"} in dump_args
        assert {"bq1": "data2"} in dump_args


@patch("bot.utils.local_db_utils.local_udb", "local_udb.pkl")
def test_save2db_lcl2_none(mock_bot, mock_pickle_dump, mock_list_to_str):
    mock_bot.temp_users = ["user1", "user2"]
    mock_list_to_str.return_value = "user1 user2"

    with patch("builtins.open", mock_open()) as mock_file:
        save2db_lcl2(None)

        mock_file.assert_called_once_with("local_udb.pkl", "wb")
        mock_list_to_str.assert_called_once_with(["user1", "user2"])

        dump_args = [args[0] for args, kwargs in mock_pickle_dump.call_args_list]
        assert "user1 user2" in dump_args


@patch("bot.utils.local_db_utils.local_rdb", "local_rdb.pkl")
def test_save2db_lcl2_rss(mock_bot, mock_pickle_dump):
    mock_bot.rss_dict = {"rss1": "data1"}

    with patch("builtins.open", mock_open()) as mock_file:
        save2db_lcl2("rss")

        mock_file.assert_called_once_with("local_rdb.pkl", "wb")

        dump_args = [args[0] for args, kwargs in mock_pickle_dump.call_args_list]
        assert {"rss1": "data1"} in dump_args


@patch("bot.utils.local_db_utils.local_cdb", "local_cdb.pkl")
def test_save2db_lcl2_cus_rename(mock_bot, mock_pickle_dump):
    mock_bot.custom_rename = "format1"

    with patch("builtins.open", mock_open()) as mock_file:
        save2db_lcl2("cus_rename")

        mock_file.assert_called_once_with("local_cdb.pkl", "wb")

        dump_args = [args[0] for args, kwargs in mock_pickle_dump.call_args_list]
        assert "format1" in dump_args

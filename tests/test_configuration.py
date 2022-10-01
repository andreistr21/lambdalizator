import json
from os import environ
from unittest.mock import MagicMock, patch

from lbz.aws_ssm import SSM
from lbz.configuration import ConfigValue, EnvValue, SSMValue


class MyConfigValue(ConfigValue):
    def getter(self) -> str:
        return "test-value"


class MyNoneConfigValue(ConfigValue):
    def getter(self) -> None:
        return None


class TestBaseConfig:
    def test_if_getter_was_used(
        self,
    ) -> None:
        cfg = MyConfigValue("key")

        assert cfg.value == "test-value"

    def test_returns_default_when_no_value_set(self) -> None:
        cfg = MyNoneConfigValue("test", default=42, parser=int)

        assert cfg.value == 42

    def test_if_parser_was_used(self) -> None:
        class MyIntConfigValue(ConfigValue):
            def getter(self) -> int:
                return 1

        cfg = MyIntConfigValue("key", parser=str)

        assert cfg.value == "1"

    @patch.object(MyConfigValue, "getter", autospec=True)
    def test_if_getter_was_used_only_once(self, mocked_getter: MagicMock) -> None:
        mocked_getter.return_value = "42"
        cfg = MyConfigValue("key")

        assert cfg.value == "42"

        mocked_getter.assert_called_once()


class TestEnvConfig:
    @patch.dict(environ, {"RANDOM_VAR": "12.2.1"}, clear=True)
    def test_gets_value_from_env(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR")

        assert env_cfg.value == "12.2.1"

    @patch.dict(environ, {"RANDOM_VAR": "12"}, clear=True)
    def test_gets_value_from_env_with_int_parser(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR", parser=int)

        assert env_cfg.value == 12

    @patch.dict(environ, {"RANDOM_VAR": "12"}, clear=True)
    def test_gets_value_from_env_with_list_parser(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR", parser=list)

        assert env_cfg.value == ["1", "2"]

    @patch.dict(environ, {"RANDOM_VAR": '{"test": "ttt"}'}, clear=True)
    def test_gets_value_from_env_with_json_parser(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR", parser=json.loads)

        assert env_cfg.value == {"test": "ttt"}


class TestSSMConfig:
    @patch.object(SSM, "get_parameter")
    def test_getter_calls_ssn_with_specific_key(self, mocked_get_parameter: MagicMock) -> None:
        mocked_get_parameter.return_value = "test_value"
        cfg = SSMValue("path/to/key")

        assert cfg.value == "test_value"

        mocked_get_parameter.assert_called_once_with("path/to/key")
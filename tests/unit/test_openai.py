"""Unit tests for the OpenAI microservice."""
# pylint: disable=redefined-outer-name
from unittest import mock

import pytest
import pytest_mock

from linguaweb_api.core import config
from linguaweb_api.microservices import openai

settings = config.get_settings()
OPENAI_GPT_MODEL = settings.OPENAI_GPT_MODEL


class MockedMessage:
    """A mocked message object."""

    def __init__(self, content: str) -> None:
        """Initializes a new instance of the MockedMessage class.

        Args:
            content: The content of the message.
        """
        self.content = content


class MockedChoice:
    """A mocked choice object."""

    def __init__(self, message: MockedMessage) -> None:
        """Initializes a new instance of the MockedChoice class.

        Args:
            message: The message of the choice.
        """
        self.message = message


class MockedOpenAiResponse:
    """A mocked OpenAI response object."""

    def __init__(self, choices: list[MockedChoice]) -> None:
        """Initializes a new instance of the MockedOpenAiResponse class.

        Args:
            choices: The choices of the response.
        """
        self.choices = choices


@pytest.fixture()
def mock_openai_client(
    mocker: pytest_mock.MockerFixture,
) -> mock.MagicMock:
    """Fixture to mock the OpenAI client."""
    mock_client = mock.MagicMock()
    mocked_response = MockedOpenAiResponse(
        choices=[
            MockedChoice(message=MockedMessage(content="Mocked response")),
        ],
    )
    mock_client.chat.completions.create.return_value = mocked_response
    mocker.patch("openai.OpenAI", return_value=mock_client)
    return mock_client


@pytest.fixture()
def gpt_instance(
    mock_openai_client: mock.MagicMock,
) -> openai.GPT:
    """Fixture to create a GPT instance with a mocked OpenAI client."""
    return openai.GPT()


@pytest.mark.asyncio()
async def test_gpt_run_method(
    gpt_instance: openai.GPT,
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Test the GPT run method returns the correct response."""
    system_prompt = "Test system message"
    user_prompt = "Test user message"
    expected_response = "Mocked response"
    mocker.patch.object(
        gpt_instance.client,
        "chat.completions.create",
        return_value={
            "choices": [{"message": {"content": expected_response}}],
        },
    )

    actual_response = await gpt_instance.run(
        prompt=user_prompt,
        system_prompt=system_prompt,
    )

    gpt_instance.client.chat.completions.create.assert_called_once_with(  # type: ignore[attr-defined]
        model=OPENAI_GPT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    assert (
        actual_response == expected_response
    ), "The run method should return the expected mocked response"


def test_load_prompts() -> None:
    """Test that the prompts are loaded correctly."""
    prompts = openai.Prompts.load()

    assert prompts.user is None
    assert isinstance(prompts.system, dict)

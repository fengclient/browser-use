from pydantic import BaseModel

from browser_use.llm.messages import UserMessage
from browser_use.llm.openai.chat import ChatOpenAI


class AnswerFormat(BaseModel):
	answer: str


async def test_openai_extra_body_is_passed_to_plain_completion(httpserver):
	httpserver.expect_request('/v1/chat/completions', method='POST').respond_with_json(
		{
			'id': 'chatcmpl-test',
			'object': 'chat.completion',
			'created': 0,
			'model': 'deepseek-v4-flash-260425',
			'choices': [
				{
					'index': 0,
					'message': {'role': 'assistant', 'content': 'ok'},
					'finish_reason': 'stop',
				}
			],
			'usage': {'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2},
		}
	)

	llm = ChatOpenAI(
		model='deepseek-v4-flash-260425',
		api_key='test-key',
		base_url=httpserver.url_for('/v1'),
		extra_body={
			'thinking': {'type': 'disabled'},
			'provider_options': {'volcengine': {'trace_id': 'test-extra-body'}},
		},
	)

	result = await llm.ainvoke([UserMessage(content='hello')])

	request, _ = httpserver.log[-1]
	body = request.get_json()
	assert result.completion == 'ok'
	assert body['thinking'] == {'type': 'disabled'}
	assert body['provider_options'] == {'volcengine': {'trace_id': 'test-extra-body'}}


async def test_openai_extra_body_is_passed_to_structured_completion(httpserver):
	httpserver.expect_request('/v1/chat/completions', method='POST').respond_with_json(
		{
			'id': 'chatcmpl-test',
			'object': 'chat.completion',
			'created': 0,
			'model': 'deepseek-v4-flash-260425',
			'choices': [
				{
					'index': 0,
					'message': {'role': 'assistant', 'content': '{"answer": "ok"}'},
					'finish_reason': 'stop',
				}
			],
			'usage': {'prompt_tokens': 1, 'completion_tokens': 3, 'total_tokens': 4},
		}
	)

	llm = ChatOpenAI(
		model='deepseek-v4-flash-260425',
		api_key='test-key',
		base_url=httpserver.url_for('/v1'),
		dont_force_structured_output=True,
		add_schema_to_system_prompt=True,
		extra_body={
			'thinking': {'type': 'enabled'},
			'reasoning_effort': 'max',
		},
	)

	result = await llm.ainvoke([UserMessage(content='answer as JSON')], output_format=AnswerFormat)

	request, _ = httpserver.log[-1]
	body = request.get_json()
	assert result.completion.answer == 'ok'
	assert body['thinking'] == {'type': 'enabled'}
	assert body['reasoning_effort'] == 'max'

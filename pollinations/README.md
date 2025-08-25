Get token from:
https://auth.pollinations.ai/

export POLLINATIONS_TOKEN="xxxxxxxxxx"

python -u batch_test.py 2>&1 | tee result_optimize_images.txt
python -u batch_test_optimize_prompt.py 2>&1 | tee result_optimize_prompts.txt

https://github.com/pollinations/pollinations/blob/master/APIDOCS.md

https://github.com/pollinations/pollinations


## Pollinations.AI Cheatsheet for Coding Assistants

### Image Generation
Generate Image: `GET https://image.pollinations.ai/prompt/{prompt}`

### Image Models
List Models: `GET https://image.pollinations.ai/models`

### Text Generation
Generate (GET): `GET https://text.pollinations.ai/{prompt}`

### Text Generation (Advanced)
Generate (POST): `POST https://text.pollinations.ai/`

### Audio Generation
Generate Audio: `GET https://text.pollinations.ai/{prompt}?model=openai-audio&voice={voice}`

### OpenAI Compatible Endpoint
OpenAI Compatible: `POST https://text.pollinations.ai/openai`

### Text Models
List Models: `GET https://text.pollinations.ai/models`

### Real-time Feeds
Image Feed: `GET https://image.pollinations.ai/feed`
Text Feed: `GET https://text.pollinations.ai/feed`
*\* required parameter*

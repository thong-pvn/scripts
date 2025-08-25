import argparse
import pollinations

# https://pollinations.ai/

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, required=True)
args = parser.parse_args()

model = pollinations.Text(
    # https://text.pollinations.ai/models
    model="openai",
    seed=100
)

optimized_prompt_request = f"Optimize the following statement: \"{args.prompt}\", replace confusing words with simpler alternatives, keep the meaning but change the wording if needed to improve clarity and conciseness, and easy understanding, and remove the surrounding environment, background."

# print(optimized_prompt_request)
# print(f"Optimizing prompt...")

output = model.Generate(
    prompt=optimized_prompt_request
)

print(output)

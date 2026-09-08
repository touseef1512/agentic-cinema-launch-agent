import os
from dotenv import load_dotenv
from parallel import Parallel

load_dotenv()

client = Parallel(api_key=os.environ["PARALLEL_API_KEY"])

result = client.extract(
    urls=[
        "https://www.sundance.org/",
        "https://www.sxsw.com/film/",
    ],
    objective=(
        "Extract this film festival's submission deadlines, eligibility "
        "requirements, submission fees, and acquisition/programming criteria "
        "for independent films."
    ),
)
print(result)

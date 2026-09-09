# Launch Radar

Most resources for independent filmmakers focus heavily on getting a movie made. Launch Radar focuses entirely on getting it seen. The application helps filmmakers navigate the fragmented and often opaque landscape of festival submissions and distribution acquisitions by building a targeted, research-backed strategy for their specific project.

### How it works

The core engine relies on a multi-stage autonomous research pipeline. When a user submits their film's profile, the system triggers the Parallel API to execute a broad web search for active festivals and distributors. It then uses the Find All capability to sift through the search results and identify viable organizations actively accepting submissions. Finally, the Extract tool pulls the literal submission guidelines, deadlines, and eligibility criteria directly from each organization's official website.

Once the raw data is gathered, it is fed into a Gemini language model using the google-genai SDK. The model synthesizes the extracted criteria against the user's specific film profile to output a structured memo containing ranked candidates, clear rationale, and actionable next steps. 

### Technology stack

The application is built on a lightweight Flask backend that manages the asynchronous research jobs. It uses the Parallel API for all web research and data extraction, and Google's Gemini models for final strategy synthesis. The frontend is built with vanilla HTML, CSS, and JavaScript. The entire application is designed to be easily deployed on a platform like Render.

### Running locally

To run the application on your own machine, you will need active API keys for both Gemini and Parallel.

Create a .env file in the repository root and add your keys:
GEMINI_API_KEY=your_key_here
PARALLEL_API_KEY=your_key_here

Install the required dependencies from the requirements file:
pip install -r requirements.txt

Start the local Flask development server:
python app.py

### Live deployment

The application is hosted and available to use at https://launch-radar-it0z.onrender.com/


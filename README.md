# Assistant Usage Guide

This assistant is built following the guidelines provided in [this tutorial](https://www.youtube.com/watch?v=DjuXACWYkkU). The following steps will guide you through setting up and running the assistant on your local machine.

## Getting Started

1. **Clone the Repository**
   Begin by cloning the repository to your local machine. Use the following command in your terminal:

   ```bash
   git clone <repository-url>
    ```

2. **Navigate to the Repository**
    Change your current working directory to the root of the cloned repository:
    ```bash
    cd assistant
    ```

3. **Install Dependencies**
    Install the required Python dependencies listed in the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

4. **Environment Setup**
    Create a .env file in the root directory of the project. This file should contain your OpenAI API key:
    ```bash
    OPENAI_API_KEY=your_api_key_here
    ```
    
5. **Run the Application**
    Start the assistant by running the `main.py` script:
    ```bash
    python main.py
    ```

6. **python main.py**
    Once the application is running, you can interact with the assistant by navigating to the following URL in your web browser:
    ```bash
    http://localhost:8000/assistant/playground/
    ```

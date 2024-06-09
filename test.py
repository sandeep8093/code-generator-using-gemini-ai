import os
import zipfile
import google.generativeai as genai
import shutil

# Your Google API key
GOOGLE_API_KEY = "API_KEY"


def get_user_input():
    """Function to take input from the user on what they want to build/generate."""
    project_description = input("Describe the project you want to build: ")
    return project_description

def generate_file_structure(project_description):
    """Function to interact with Gemini AI to generate file structure and initial files."""
    prompt = f"Generate a detailed file structure  for the following project: {project_description} with no explanation and atmost 15 files"
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    file_structure = ""
    for chunk in response:
        file_structure += chunk.text
    return file_structure.strip()

def create_directories_files(file_structure, project_description):
    """Function to create the directory structure and files based on the provided file and folder structure."""
    project_path = 'generated_project'
    # Delete the existing directory if it exists
    if os.path.exists(project_path):
        shutil.rmtree(project_path)
    print("Creating directories and files...")
    os.makedirs('generated_project', exist_ok=True)
    
    # Split the file_structure by line
    lines = file_structure.split('\n')
    dir_stack = ['generated_project']

    for line in lines:
        if line == '' or line.startswith('```'):
            continue
        
        name =  line.split()
        depth = line.count('│')
    
        # Ensure the stack is at the correct depth
        while len(dir_stack) > depth + 1:
            dir_stack.pop()
        
        # Check if it's a directory or file
        if '.' not in name[-1]:
            full_dir_path = os.path.join(dir_stack[-1], name[-1])
            os.makedirs(full_dir_path, exist_ok=True)
            print(f"Directory created: {full_dir_path}")
            # Update the current directory
            dir_stack.append(full_dir_path)
           
        else:
            full_file_path = os.path.join(dir_stack[-1], name[-1])
            prompt = f"Generate the content for the following file as part of the project described: {project_description}. File: {full_file_path} with  no explanation"
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            file_content = ""
            for chunk in response:
                file_content += chunk.text
            with open(full_file_path, 'w') as file:
                file.write(file_content.strip())
                print(f"Content added to file: {full_file_path}")
            print(f"File created: {full_file_path}")
    print("Directories and files created successfully.")



def zip_project():
    """Function to zip the generated project."""
    zip_path = 'generated_project.zip'
    # Delete the existing zip file if it exists
    if os.path.exists(zip_path):
        os.remove(zip_path)

    with zipfile.ZipFile('generated_project.zip', 'w') as zipf:
        for root, dirs, files in os.walk('generated_project'):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                       os.path.join('generated_project', '..')))


def main():
    project_description = get_user_input()
    print("Generating file structure...")
    file_structure = generate_file_structure(project_description)
    print(file_structure)
    print("File structure generated.")
    create_directories_files(file_structure, project_description)
    print("Directories and files with content created.")
    zip_project()
    print("Project has been generated and zipped as 'generated_project.zip' in the current directory.")

if __name__ == "__main__":
    main()

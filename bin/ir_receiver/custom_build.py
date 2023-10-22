Import("env")

# Define the custom build command
custom_build_command = "g++ -o my_win32_app.exe my_win32_app.c -mwindows"

# Run the custom build command
print("Running custom build command: " + custom_build_command)
env.Execute(custom_build_command)
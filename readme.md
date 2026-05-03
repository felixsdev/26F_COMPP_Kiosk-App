# DI Kiosk

## Setup Instructions

This project requires a local `data` directory to store session and context information. Because this folder contains dynamic/private data, it is not tracked by Git. 

Before running the application, please complete the following steps:

1. Create a folder named `data` in the root directory of the project.
2. Inside the `data` folder, create the following three files:
   - `session.json` (Initialize with `[]`)
   - `context.json` (Initialize with `{}`)
   - `history.json` (Initialize with `[]`)
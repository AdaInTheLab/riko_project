# Google Drive Connector

## Description
A specialized interface module for the Human Pattern Lab that grants an OpenClaw agent the capability to interact with the Google Drive API. This skill enables the retrieval, search, and deep-reading of documents stored within the user's cloud-based file system.

## Instructions
1. This skill requires valid Google Cloud Project credentials (OAuth 2.0).
2. The user must authorize the agent to access their Google Drive data.
3. Use the provided tools to index, query, or extract textual data from stored patterns (files).
4. All operations should be conducted with laboratory-grade precision.

## Tools

### list_files
Lists files within a specified directory or the root of the Google Drive.
- **Parameters**: 
    - `directory_id` (string, optional): The ID of the folder to list. Defaults to root.
    - `max_results` (integer, optional): Maximum number of files to return.

### read_file_content
Retrieves the textual content of a specific Google Doc or binary file.
- **Parameters**:
    - `file_id` (string, required): The unique identifier of the file.
    - `mime_type` (string, optional): Specify the format for export (e.g., text/plain).

### search_files
Performs a semantic or keyword-based search across the user's Drive using the Google search query syntax.
- **Parameters**:
    - `query` (string, required): The search string (e.g., "name contains 'pattern'").
    - `include_trashed` (boolean, optional): Whether to include files in the trash.

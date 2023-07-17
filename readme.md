<h1>WebVTT Subtitle Management API Documentation</h1>

This API provides endpoints for managing WebVTT subtitle files and captions. It allows users to upload video and subtitle files, insert captions, update captions, delete captions, and display subtitle files.

<h3>Routes</h3>

1. Upload File

    Route: /save-file\
    Method: POST\
    Description: Uploads a file(video or subtitle) to the server.\
    Request Parameters: None\
    Request Body:\
        file (file): The file to be uploaded.\
    Response:\
        Success: HTTP 200 OK\
            Response Body: {'status': 'success', 'message': 'file uploaded'}\
        Failure: HTTP 400 Bad Request\
            Response Body:\
                {'status': 'failure', 'message': 'no file sent'} (if no file was sent)\
                {'status': 'failure', 'message': 'no file selected for upload'} (if no file was selected)\
                {'status': 'failure', 'message': 'allowed filetypes are .mp4, .vtt, .srt'} (if the file type is not allowed)

2. Display File

    Route: /display/<file_name>\
    Method: GET\
    Description: Displays a file stored on the server.\
    Request Parameters:\
        file_name (string): The name of the file to be displayed.\
    Response:\
        Success: HTTP 200 OK\
            The file is returned.\
        Failure: HTTP 404 Not Found\
            Response Body: {'status': 'failure', 'message': 'file not found'}

3. Insert Caption

    Route: /insert-caption\
    Method: PUT\
    Description: Inserts a caption into a WebVTT subtitle file.\
    Request Parameters: None\
    Request Body:\
        fileName (string): The name of the WebVTT subtitle file.\
        captionStartTime (string): The start time of the caption (in the format hh:mm:ss.ttt).\
        captionEndTime (string): The end time of the caption (in the format hh:mm:ss.ttt).\
        captionContent (string): The content of the caption.\
    Response:\
        Success: HTTP 200 OK\
            Response Body: {'status': 'success', 'message': 'updated caption'}\
        Failure: HTTP 400 Bad Request\
            Response Body:\
                {'status': 'failure', 'message': 'no captions sent'} (if no captions were sent)\
                {'status': 'failure', 'message': 'allowed timestamp format is hh:mm:ss.ttt'} (if the timestamp format is incorrect)

4. Create Subtitle File

    Route: /create-subtitle\
    Method: POST\
    Description: Creates a new WebVTT subtitle file.\
    Request Parameters: None\
    Request Body:\
        fileName (string): The name of the subtitle file.\
    Response:\
        Success: HTTP 200 OK\
            Response Body: {'status': 'success', 'message': 'created new subtitle file'}\
        Failure: HTTP 400 Bad Request\
            Response Body: {'status': 'failure', 'message': 'subtitle file already present'}

5. Delete Caption

    Route: /delete-caption\
    Method: POST\
    Description: Deletes a specific caption from a WebVTT subtitle file.\
    Request Parameters: None\
    Request Body:\
        fileName (string): The name of the WebVTT subtitle file.\
        startTime (string): The start time of the caption to be deleted (in the format hh:mm:ss.ttt).\
        endTime (string): The end time of the caption to be deleted (in the format hh:mm:ss.ttt).\
        content (string): The content of the caption to be deleted.\
    Response:\
        Success: HTTP 200 OK\
            Response Body: {'status': 'success', 'message': 'selected subtitle deleted'}\
        Failure: HTTP 400 Bad Request\
            Response Body:\
                {'status': 'failure', 'message': 'could not delete subtitle'} (if the caption deletion fails)\
                {'status': 'failure', 'message': 'could not find subtitle to delete'} (if the specified caption is not found)

6. Update Caption

    Route: /update-caption\
    Method: POST\
    Description: Updates the content of a specific caption in a WebVTT subtitle file.\
    Request Parameters: None\
    Request Body:\
        fileName (string): The name of the WebVTT subtitle file.\
        startTime (string): The start time of the caption to be updated (in the format hh:mm:ss.ttt).\
        endTime (string): The end time of the caption to be updated (in the format hh:mm:ss.ttt).\
        content (string): The updated content of the caption.\
    Response:\
        Success: HTTP 200 OK\
            Response Body: {'status': 'success', 'message': 'selected subtitle updated'}\
        Failure: HTTP 400 Bad Request\
            Response Body:\
                {'status': 'failure', 'message': 'could not update subtitle'} (if the caption update fails)\
                {'status': 'failure', 'message': 'could not find subtitle to update'} (if the specified caption is not found)\
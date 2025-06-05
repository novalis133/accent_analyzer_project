import tempfile
from video_utils import download_and_extract_audio
import os

# Test the Previously failing URL
test_url = 'https://youtu.be/TkyeUckXc-0?si=7agVr2hjn66mSc2J'
temp_dir = tempfile.mkdtemp()
print(f'Testing URL: {test_url}')
print(f'Temp directory: {temp_dir}')

result = download_and_extract_audio(test_url, temp_dir)
print(f'Result: {result}')

if result:
    print(f'SUCCESS! WAV file created: {result}')
    if os.path.exists(result):
        file_size = os.path.getsize(result)
        print(f'File size: {file_size} bytes')
else:
    print('FAILED - No WAV file created')
    
# Show temp directory contents
print(f'Contents of {temp_dir}:')
for f in os.listdir(temp_dir):
    fp = os.path.join(temp_dir, f)
    size = os.path.getsize(fp) if os.path.isfile(fp) else 'DIR'
    print(f'  {f}: {size} bytes') 
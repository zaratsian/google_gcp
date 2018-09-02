


#############################################################################
#
#   Google Cloud Vision / Image Analysis
#
#   Usage:  file.py --youtube_url YOUTUBE_URL --bucket_name BUCKET_NAME --bq_dataset_id BQ_DATASET_ID --bq_table_id BQ_TABLE_ID
#           file.py --youtube_url=https://www.youtube.com/watch?v=imm6OR605UI --bucket_name=zmiscbucket1 --bq_dataset_id=video_analysis1 --bq_table_id=video_metadata1
#           file.py --youtube_url=https://www.youtube.com/watch?v=7dKownfx75E --bucket_name=zmiscbucket1 --bq_dataset_id=video_analysis1 --bq_table_id=video_metadata1
#
#   Dependencies:
#       pip install --upgrade google-cloud-vision
#       pip install --upgrade google-cloud-storage
#       pip install --upgrade google-cloud-bigquery
#       pip install pytube
#
#   References:
#       https://cloud.google.com/vision/docs/libraries
#       https://github.com/nficano/pytube
#
#############################################################################



import os,sys
import io
import datetime
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import storage
from google.cloud import bigquery



def bg_streaming_insert(rows_to_insert, bq_dataset_id, bq_table_id):
    ''' BigQuery Streaming Insert - Insert python list into BQ '''
        
    # Note: The table must already exist and have a defined schema
    # rows_to_insert is a list of variables (i.e. (id, date, value1, value2, etc.))
    print('[ INFO ] Inserting records in BigQuery')
    client    = bigquery.Client()
    table_ref = client.dataset(bq_dataset_id).table(bq_table_id)
    table     = client.get_table(table_ref)
    errors    = client.insert_rows(table, rows_to_insert)
    if errors == []:
        print('[ INFO ] Complete. No errors on Big Query insert')



def image_label_detection(image_filepath):
    
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    
    # Loads the image into memory
    with io.open(image_filepath, 'rb') as image_file:
        content = image_file.read()
    
    image = types.Image(content=content)
    
    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations
        
    print('Labels:')
    for label in labels:
        print(label.description)



def image_tag_web_entities(image_filepath):
    """Detects web annotations given an image."""
    
    client = vision.ImageAnnotatorClient()
    
    with io.open(image_filepath, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.types.Image(content=content)
    
    # Uncomment - Use these two lines to score images within a GCS uri 
    #image = vision.types.Image()
    #image.source.image_uri = uri
    
    response = client.web_detection(image=image)
    annotations = response.web_detection
    
    '''
    if annotations.best_guess_labels:
        for label in annotations.best_guess_labels:
            print('\nBest guess label: {}'.format(label.label))
    '''
    
    '''
    if annotations.pages_with_matching_images:
        print('\n{} Pages with matching images found:'.format(len(annotations.pages_with_matching_images)))
        
        for page in annotations.pages_with_matching_images:
            print('\n\tPage url   : {}'.format(page.url))
            
            if page.full_matching_images:
                print('\t{} Full Matches found: '.format(
                       len(page.full_matching_images)))
                
                for image in page.full_matching_images:
                    print('\t\tImage url  : {}'.format(image.url))
            
            if page.partial_matching_images:
                print('\t{} Partial Matches found: '.format(
                       len(page.partial_matching_images)))
                
                for image in page.partial_matching_images:
                    print('\t\tImage url  : {}'.format(image.url))
    '''
    
    image_web_entities = []
    if annotations.web_entities:
        
        datetimeid = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        print('\n{} Web entities found: '.format(len(annotations.web_entities)))
        
        for entity in annotations.web_entities:
            print('\n\tScore      : {}'.format(entity.score))
            print(u'\tDescription: {}'.format(entity.description))
            image_web_entities.append( (datetimeid, image_filepath, entity.description, entity.score) )
    
    '''
    if annotations.visually_similar_images:
        print('\n{} visually similar images found:\n'.format(len(annotations.visually_similar_images)))
        
        for image in annotations.visually_similar_images:
            print('\tImage url    : {}'.format(image.url))
    '''
    
    return image_web_entities






if __name__ == "__main__":
    
    image_filepath = sys.argv[1]
    
    image_label_detection(image_filepath)
    
    image_tag_web_entities(image_filepath)



#ZEND

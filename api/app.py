from flask import Flask, jsonify, request
from flask_cors import CORS
from joblib import load
from flask import render_template
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pickle
import nltk
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer 
import re
import openai
import os   
# Download the stopwords resource
nltk.download('stopwords')

presence_classifier = load('presence_classifier.joblib')
presence_vect = load('presence_vectorizer.joblib')
category_classifier = load('category_classifier.joblib')
category_vect = load('category_vectorizer.joblib')

app = Flask(__name__)
CORS(app)


import google.generativeai as genai

genai.configure(api_key="AIzaSyAjR9w20b_YGZDkeyw19YeUJQkNd-_qLgk")


generation_config = {
  "temperature": 0.7,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


# @app.route('/', methods=['POST'])

# def identify_dark_patterns(text):
#     prompt = f"Analyze this text: {text} Does it employ manipulative tactics to influence my behavior or choices? If so, identify the specific dark patterns (Social Proof, Urgency, Misdirection, Scarcity, Obstruction) present and explain how they are used, considering the sentiment and stylistic elements you identified."

#     response = openai.Completion.create(
#         engine="text-davinci-003",  # Adjust model based on your needs
#         prompt=prompt,
#         max_tokens=1024,
#         n=1,
#         stop=None,
#         temperature=0.5,
#     )

#     return response.choices[0].text


def main():
    if request.method == 'POST':
        output = []
        data = request.get_json().get('tokens')
        # i = 0 
        for token in data:
            # print('hi')
            # print(presence_vect.transform([token]))
            result = presence_classifier.predict(presence_vect.transform([token]))
            if result == 'Dark':
                cat = category_classifier.predict(category_vect.transform([token]))
                output.append(cat[0])
            else:
                output.append(result[0])
            # i += 1
            # if i < 50:
            #     print(token, output[-1])
                # print(identify_dark_patterns(str(token)))

        dark = [data[i] for i in range(len(output)) if output[i] == 'Dark']
        for d in dark:
            print(d)
        print()
        print(len(dark))

        message = '{ \'result\': ' + str(output) + ' }'
        print(message)

        json = jsonify(message)

        return json






####reviews#####


def get_reviews(url):    
    # Header to set the requests as a browser requests
    headers = {
        'authority': 'www.amazon.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    # URL of The amazon Review page
    reviews_url = url

    # Define Page No
    len_page = 4

    # Extra Data as Html object from amazon Review page
    def reviewsHtml(url, len_page):
        
        # Empty List define to store all pages html data
        soups = []
        
        # Loop for gather all 3000 reviews from 300 pages via range
        for page_no in range(1, len_page + 1):
            
            # parameter set as page no to the requests body
            params = {
                'ie': 'UTF8',
                'reviewerType': 'all_reviews',
                'filterByStar': 'critical',
                'pageNumber': page_no,
            }
            
            # Request make for each page
            response = requests.get(url, headers=headers)
            
            # Save Html object by using BeautifulSoup4 and lxml parser
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Add single Html page data in master soups list
            soups.append(soup)
            
        return soups

    # Grab Reviews name, description, date, stars, title from HTML
    def getReviews(html_data):

        # Create Empty list to Hold all data
        data_dicts = []
        
        # Select all Reviews BOX html using css selector
        boxes = html_data.select('div[data-hook="review"]')
        
        # Iterate all Reviews BOX 
        for box in boxes:
            
            # Select Name using css selector and cleaning text using strip()
            # If Value is empty define value with 'N/A' for all.
            try:
                name = box.select_one('[class="a-profile-name"]').text.strip()
            except Exception as e:
                name = 'N/A'

            try:
                stars = box.select_one('[data-hook="review-star-rating"]').text.strip().split(' out')[0]
            except Exception as e:
                stars = 'N/A'   

            try:
                title = box.select_one('[data-hook="review-title"]').text.strip()
            except Exception as e:
                title = 'N/A'

            try:
                # Convert date str to dd/mm/yyy format
                datetime_str = box.select_one('[data-hook="review-date"]').text.strip().split(' on ')[-1]
                date = datetime.strptime(datetime_str, '%B %d, %Y').strftime("%d/%m/%Y")
            except Exception as e:
                date = 'N/A'

            try:
                description = box.select_one('[data-hook="review-body"]').text.strip()
            except Exception as e:
                description = 'N/A'

            # create Dictionary with al review data 
            data_dict = {
                'Name' : name,
                'Stars' : stars,
                'Title' : title,
                'Date' : date,
                'Description' : description
            }

            # Add Dictionary in master empty List
            data_dicts.append(data_dict)
        
        return data_dicts

    # Grab all HTML
    html_datas = reviewsHtml(reviews_url, len_page)

    # Empty List to Hold all reviews data
    reviews = []

    # Iterate all Html page 
    for html_data in html_datas:
        
        # Grab review data
        review = getReviews(html_data)
        
        # add review data in reviews empty list
        reviews += review

    # Create a dataframe with reviews Data
    df_reviews = pd.DataFrame(reviews)
    return df_reviews






def classify_review(review):
    # Load the model and vectorizer
    model = pickle.load(open('best_model.pkl','rb'))
    vectorizer = pickle.load(open('count_vectorizer.pkl','rb'))
    
    # Define stopwords
    sw = set(stopwords.words('english'))
    
    # Define text preprocessing function
    def text_preprocessing(text):
        txt = TextBlob(text)
        result = txt.correct()
        removed_special_characters = re.sub("[^a-zA-Z]", " ", str(result))
        tokens = removed_special_characters.lower().split()
        stemmer = PorterStemmer()

        cleaned = []
        stemmed = []

        for token in tokens:
            if token not in sw:
                cleaned.append(token)

        for token in cleaned:
            token = stemmer.stem(token)
            stemmed.append(token)

        return " ".join(stemmed)
    
    # Define text classification function
    def text_classification(text):
        if len(text) < 1:
            return "No input provided."
        else:
            cleaned_review = text_preprocessing(text)
            process = vectorizer.transform([cleaned_review]).toarray()
            prediction = model.predict(process)
            return "The review entered is Legitimate." if prediction[0] else "The review entered is Fraudulent."

    print("Review entered: ", review)
    return text_classification(review)


def filter_legit_reviews(df_reviews, classify_review):
    legit_reviews = pd.DataFrame(columns=df_reviews.columns)
    
    for i in range(len(df_reviews)):
        if classify_review(df_reviews['Description'][i]) == "The review entered is Legitimate.":
            legit_reviews = legit_reviews.append(df_reviews.iloc[i])

    return legit_reviews

@app.route('/reviews', methods=['GET'])
def handle_get_reviews():
    # Get the URL from the request
    url = request.args.get('url')
    print(url)
    # url = "https://www.amazon.in/ASIAN-Wonder-Firozi-Sports-Indian/dp/B01N3CW73G/ref=sr_1_7?crid=1NDG1T62UG9OW&keywords=shoes&qid=1707281802&sprefix=shoes%2Caps%2C619&sr=8-7&th=1&psc=1"
    
    # Call the get_reviews function with the provided URL
    df_reviews = get_reviews(url)
    legit_reviews = filter_legit_reviews(df_reviews, classify_review)
    legit_reviews_html = legit_reviews.to_html()
    
    folder_path = "/Users/rohan/Desktop/Dark-Trends-Prod/app"
    file_name = "reviews.html"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Combine folder path and file name to get the full file path
    file_path = os.path.join(folder_path, file_name)
    
    # Write content to the file
    with open(file_path, 'w') as file:
        file.write(legit_reviews_html)

    return render_template(legit_reviews_html)
    
    # Print the reviews in the terminal

    #

@app.route('/privacy', methods=['GET'])
#Loading...
def privacy():
    url = request.args.get('url')
    prompt_parts = [
    "\"Summarize the privacy policy of the website IN BULLET POINTS, INTIALLY MENTION PRIVACY POLICY OF WHICH WEBSITE, ADD SPACES AFTER NEW POINTS"+ url +". After summarizing, provide a rating for the privacy policy based on the following criteria: transparency, data collection practices, user control options, and overall clarity. Use a scale from 1 to 5, with 5 being the highest rating indicating excellent privacy practices and 1 being the lowest indicating poor privacy practices. Please ensure that the summary and rating are concise and informative. \"",
    ]

    response = model.generate_content(prompt_parts)
    
    return jsonify({"policy": response.text})


# Create a route to execute the get_reviews function and pass the DataFrame to the HTML template
# @app.route('/')
# def index():
#     # Assume legit_reviews is the DataFrame containing legitimate reviews
#     legit_reviews = pd.DataFrame(columns=['Name', 'Stars', 'Date', 'Description'])
    
#     # Convert the DataFrame to JSON string
#     legit_reviews_json = legit_reviews.to_json(orient='records')
    
#     # Pass the JSON string to the template
#     return render_template('/Users/rohan/Desktop/Dark-Trends-Prod-main-2/app/reviews.html', legit_reviews_json=legit_reviews_json)

  
if __name__ == '__main__':
    app.run(threaded=True, debug=True)




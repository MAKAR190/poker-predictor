import cv2
import numpy as np
import os
from PIL import Image
from calculating_win_rate import calculate_win_rate
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext


# Define your bot's API token here
TOKEN = "6360090843:AAHRnxy4pAT3Rbmh_yrgzHI-Tqec855btO8"

# Set up the Telegram bot
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

matched_cards_table = []  # Define these variables here
matched_cards_hand = []   # Define these variables here

def handle_photo(update, context):
    global matched_cards_table, matched_cards_hand
    user_id = update.message.from_user.id
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(f'{user_id}_temp_photo.jpg')

    # Now, you can process the downloaded photo or do whatever you need with it.
    resize_image_table(f'{user_id}_temp_photo.jpg', "poker_cropped.jpg", (712, 308))
    resize_image_hand(f'{user_id}_temp_photo.jpg', "my_hand_cropped.jpg", (712, 308))
    # After processing, you can delete the downloaded file if needed.
    os.remove(f'{user_id}_temp_photo.jpg')

    # Load a screenshot image
    screenshot_table = cv2.imread('poker_cropped.jpg')
    screenshot_hand = cv2.imread('my_hand_cropped.jpg')
    
    # List all image files in the "cards" subfolder
    card_files = [file for file in os.listdir('cards') if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]

    # Create the card_templates list by adding the folder path to each image file
    card_templates = [os.path.join('cards', file) for file in card_files]

    # Initialize a dictionary to store detected cards with the highest matching score
    detected_cards_table = {}
    detected_cards_hand = {}

    # Create a copy of the screenshot for annotation
    annotated_screenshot_table = screenshot_table.copy()
    annotated_screenshot_hand = screenshot_hand.copy()

    for template_file in card_templates:
        # Load the template image
        template = cv2.imread(template_file)

        # Match the template in the screenshot using template matching
        result_table = cv2.matchTemplate(screenshot_table, template, cv2.TM_CCOEFF_NORMED)
        result_hand = cv2.matchTemplate(screenshot_hand, template, cv2.TM_CCOEFF_NORMED)

        # Define a threshold for matching results
        threshold = 0.9

        # Find locations where the template matches above the threshold
        locations_table = np.where(result_table >= threshold)
        locations_hand = np.where(result_hand >= threshold)

        for pt in zip(*locations_hand[::-1]):
            # Extract the rank and suit from the template file name
            # Extract the rank and suit from the template file name using the first two parts
            _, filename = os.path.split(template_file)
            parts = filename.rsplit('_', 2)  # Split into at most three parts
            if len(parts) >= 2:
                rank, suit_with_extension = parts[:2]
                suit = suit_with_extension.split('.')[0]  # Remove the '.jpg' extension
            else:
                # Handle cases where there is not enough parts after splitting
                rank, suit = filename, ""

            score = result_hand[pt[1], pt[0]]

            # Check if a card with the same rank has already been detected
            if rank in detected_cards_hand:
                # Check if the current suit has a higher matching score
                if score > detected_cards_hand[rank][0]:
                    detected_cards_hand[rank] = (score, template_file)
                    matched_cards_hand.append((rank, suit))

            else:
                detected_cards_hand[rank] = (score, template_file)
                matched_cards_hand.append((rank, suit))

            # Draw bounding boxes around detected cards on the annotated screenshot
            w, h, _ = template.shape
            top_left = pt
            bottom_right = (pt[0] + h, pt[1] + w)
            cv2.rectangle(annotated_screenshot_hand, top_left, bottom_right, (0, 255, 0), 2)  # Green rectangle

        # Extract the coordinates of matched regions
        for pt in zip(*locations_table[::-1]):
            # Extract the rank and suit from the template file name
            # Extract the rank and suit from the template file name using the first two parts
            _, filename = os.path.split(template_file)
            parts = filename.rsplit('_', 2)  # Split into at most three parts
            if len(parts) >= 2:
                rank, suit_with_extension = parts[:2]
                suit = suit_with_extension.split('.')[0]  # Remove the '.jpg' extension
            else:
                # Handle cases where there is not enough parts after splitting
                rank, suit = filename, ""

            score = result_table[pt[1], pt[0]]

            # Check if a card with the same rank has already been detected
            if rank in detected_cards_table:
                # Check if the current suit has a higher matching score
                if score > detected_cards_table[rank][0]:
                    detected_cards_table[rank] = (score, template_file)
                    matched_cards_table.append((rank, suit))
            else:
                detected_cards_table[rank] = (score, template_file)
                matched_cards_table.append((rank, suit))

            # Draw bounding boxes around detected cards on the annotated screenshot
            w, h, _ = template.shape
            top_left = pt
            bottom_right = (pt[0] + h, pt[1] + w)
            cv2.rectangle(annotated_screenshot_table, top_left, bottom_right, (0, 255, 0), 2)  # Green rectangle

    # Print the matched card file paths with the highest matching score
    for rank, (score, card) in detected_cards_table.items():
        print(f"Matched card: {card} with score: {score}")
    for rank, (score, card) in detected_cards_hand.items():
        print(f"Matched card: {card} with score: {score}")

    matched_cards_table = list(set(matched_cards_table))
    matched_cards_hand = list(set(matched_cards_hand))

    print(matched_cards_table)
    print(matched_cards_hand)
    # Save or return the annotated screenshot
    cv2.imwrite('annotated_poker_table.jpg', annotated_screenshot_table)
    cv2.imwrite('annotated_poker_hand.jpg', annotated_screenshot_hand)
    
    # Calculate the win rate
    win_rate = calculate_win_rate(matched_cards_hand, matched_cards_table)

    # Send annotated images with detected objects
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open('annotated_poker_table.jpg', 'rb'))
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open('annotated_poker_hand.jpg', 'rb'))

    # Send the win rate
    context.bot.send_message(chat_id=update.message.chat_id, text=f"My win rate: {win_rate:.2f}%")

dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))

def resize_image_table(input_path, output_path, target_size):
    # Open the image using Pillow
    image = Image.open(input_path)
    # Get the original image size
    original_width, original_height = image.size
    # Calculate the center coordinates
    center_x = original_width / 2
    center_y = original_height / 2
    # Calculate the cropping box
    left = center_x - target_size[0] / 2
    top = center_y - target_size[1] / 2
    right = center_x + target_size[0] / 2
    bottom = center_y + target_size[1] / 2
    # Crop and resize the image
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image = cropped_image.resize((original_width, original_height), Image.ANTIALIAS)
    # Save the resized image
    cropped_image.save(output_path)

def resize_image_hand(input_path, output_path, target_size):
    # Open the image using Pillow
    image = Image.open(input_path)
    # Get the original image size
    original_width, original_height = image.size
    # Calculate the cropping box for the right-bottom corner
    left = original_width - target_size[0]
    top = original_height - target_size[1]
    right = original_width
    bottom = original_height
    # Crop and resize the image
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image = cropped_image.resize((original_width, original_height), Image.ANTIALIAS)
    # Save the resized image
    cropped_image.save(output_path)

# Specify the path to the "cards" subfolder where your card images are located
cards_folder = 'cards'

# Start the bot
updater.start_polling()
updater.idle()

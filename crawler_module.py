from dotenv import load_dotenv
import os
import time
import re
import emoji
import spacy
from deep_translator import GoogleTranslator

load_dotenv(override=True)
nlp = spacy.load("es_core_news_sm")  # Load the Spanish spaCy model

class DataExtractor:
    def __init__(self, page):
        self.page = page
        self.username = os.getenv("INSTAGRAM_USER")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        self.output = []

    def login(self):
        self.page.goto("https://www.instagram.com/")
        try:
            self.page.wait_for_selector("button:text('Permitir todas las cookies')", timeout=5000)
            self.page.click("button:text('Permitir todas las cookies')")
            time.sleep(2)
        except:
            pass

        self.page.fill("input[name='username']", self.username)
        self.page.fill("input[name='password']", self.password)
        self.page.click("button[type='submit']")
        time.sleep(2)

        try:
            self.page.click("text='Ahora no'")
            time.sleep(2)
        except:
            pass

        try:
            self.page.click("text='Ahora no'")
            time.sleep(2)
        except:
            pass

    def access_profile(self, profile_name):
        profile_url = f"https://www.instagram.com/{profile_name}/"
        self.page.goto(profile_url)
        print(f"The Instagram profile of {profile_name} has been accessed")
        time.sleep(2)
        return profile_url

    def get_total_posts(self):
        '''Gets the number of posts the target profile has.'''
        try:
            self.page.wait_for_selector("header section ul li span", timeout=10000)
            elem_publish = self.page.query_selector("header section ul li span")
            if elem_publish:
                number = elem_publish.inner_text().strip()
                return int(re.search(r"\d+", number.replace(",", "").replace(".", "")).group())
            else:
                return 0
        except Exception as e:
            print(f"Error getting the number of posts: {e}")
            return 0

    def get_name_and_bio(self):
        '''Extacts the name and biography of the target profile.'''
        perfil_contenedor = self.page.query_selector("header")
        name_elements = perfil_contenedor.query_selector_all("div.x9f619.xjbqb8w.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek")
        name_bio_text = [el.inner_text().strip() for el in name_elements if el.inner_text().strip()]

        try:
            posibles_mas = self.page.locator("span").filter(has_text="más")
            for i in range(posibles_mas.count()):
                el = posibles_mas.nth(i)
                if el.is_visible() and el.inner_text().strip().lower() == "más":
                    print("Clicking the 'more' button")
                    el.click()
                    time.sleep(1)
                    break
        except Exception as e:
            print(f"Could not click 'more': {e}")

        bio_elements = self.page.query_selector_all("div.x7a106z")
        for bio in bio_elements:
            span_elements = bio.query_selector_all("span._ap3a._aaco._aacu._aacx._aad7._aade")
            for span in span_elements:
                new_text = span.inner_text().strip()
                if new_text:
                    name_bio_text.append(new_text)

        return self.filter_words(name_bio_text)

    def extract_posts(self, recent, activate_avoid_overloading, total_posts, number, counter, total_counter, counter_scroll):
        """
        Extract posts from a profile without losing the progress of the scroll.
        """
        # HERE WE WILL CHECK THAT THE DIFFERENCE BETWEEN THE LAST RECENT POST AND THE TOTAL NUMBER OF POSTS IS NOT > 108 TO AVOID SCROLL LOADING ERRORS
        if (recent == False) and (counter == 0) and (total_posts - total_counter > 108): # counter = 0 means we just switched to old ones
            num_scrolls = (108 // 12) + (number // 12) # Skip 108 posts and then calculate the necessary scrolls needed to extract the user input number of old posts
        elif recent == True and counter == 0:
            # SCROLLS CASE WHEN WE JUST STARTED THE DATA EXTRACTION PROCESS
            num_scrolls = 1
        elif recent == True: 
            # Calculate the remaining scrolls to be done
            if ((number + counter) // 12) < counter_scroll: # 12 because 1 scroll = 12 posts
                num_scrolls = 0
            else:
                num_scrolls = 1
        elif recent == False:
            num_scrolls = (total_posts // 12) - counter_scroll

        if num_scrolls > 0:
            print(f"Making {num_scrolls} new scrolls to load more posts...")
            for _ in range(num_scrolls):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # Scroll-down
                time.sleep(3)  # Wait for posts to load
            counter_scroll += num_scrolls  # Update the counter of scrolls made

        # Get the posts available on screen
        posts_links = self.page.query_selector_all("div.xg7h5cd.x1n2onr6 a.x1i10hfl")
        post_urls = [post.get_attribute("href") for post in posts_links if post.get_attribute("href")]
        post_urls = list(dict.fromkeys(post_urls))  # Eliminate duplicates while maintaining order

        # Determine which publications to extract
        if recent or activate_avoid_overloading == True: # If the profile still has more than 108 posts left to analize, the scroll logic will be the same as for recent posts.
            selected_posts = post_urls[counter : counter + number]  
        else: # If we are using the old ones, we must delete the last elements of the list so that they do not repeat
            selected_posts = post_urls
            i = 0
            for i in range(counter):
                selected_posts.pop()
                i += 1
            selected_posts = selected_posts[-number:]
        
        post_captions = []  # List of captions

        for post_url in selected_posts:
            if post_url:
                print(f"Accessing the post: {post_url}")
                with self.page.expect_navigation():
                    self.page.click(f'a[href="{post_url}"]')  # Click on the post 
                time.sleep(3)  # Wait post to load
                
                # Extract caption
                try:
                    caption_element = self.page.query_selector("div.xt0psk2 h1")
                    if caption_element:
                        caption_text = caption_element.inner_text().strip()
                        if caption_text:
                            post_captions.append(caption_text)
                except Exception as e:
                    print(f"Error extracting caption from {post_url}: {e}")

                # Close the post and return to the feed without reloading the page
                self.page.keyboard.press("Escape")
                time.sleep(2)  # Wait to avoid loading problems
            else:
                print("The post link was not found.")

        return post_captions, counter_scroll  # Returns posts and scroll state
    
    def filter_words(self, input_list):
        """
        Function that returns a list of filtered words, eliminating stopwords and words with a length less than 3.
        """
        new_words = " ".join(input_list).split()
        pattern = r"[^\wáéíóúüñ._]"

        for word in new_words:
            clean_word = re.sub(pattern, "", word).lower()
            separated_words = self.split_hyphen_dot(clean_word)

            for last_word in separated_words:
                if last_word and len(last_word) >= 3 and last_word not in self.output and not nlp.vocab[last_word].is_stop:
                    self.output.append(last_word)

            for char in word:
                if emoji.is_emoji(char):
                    emoji_desc = self.obtain_description_emoji(char)
                    emojis_separated = self.split_hyphen_dot(emoji_desc)
                    for final_emoji in emojis_separated:
                        if final_emoji and len(final_emoji) >= 3 and final_emoji not in self.output and not nlp.vocab[final_emoji].is_stop:
                            self.output.append(final_emoji)

        return self.output

    def obtain_description_emoji(self, emoji_str):
        '''Converts the meaning of emojis into words and translates them to Spanish.'''
        description = emoji.demojize(emoji_str).replace(":", " ").strip().lower()
        try:
            description_es = GoogleTranslator(source='en', target='es').translate(description)
            return description_es if description_es else ""
        except Exception as e:
            print(f"Error in the translation: {e}")
            return ""

    def split_hyphen_dot(self, word): 
        '''Separates the word by underscores and dots.'''
        return re.split(r'[_\.]', word)

    def start_crawler(self, social_name, profile_name):
        '''Starts the process of extracting data.'''
        if social_name == "Instagram":
            self.login()
            profile_url = self.access_profile(profile_name)
            n_posts = self.get_total_posts()
            info_name_bio = self.get_name_and_bio()
            print("Name and biography information obtained")
            return profile_url, n_posts, info_name_bio
        else:
            print("Social media not supported.")
            return None, 0, []


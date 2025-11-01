import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time
import os
from pathlib import Path

class TestParser:
    def __init__(self, headless=False):
        self.setup_driver(headless)
        self.all_questions = []
        self.progress_file = 'parsing_progress.json'
        self.progress = self.load_progress()
        
    def load_progress(self):
        """Load progress from file if exists"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"Loaded progress: {len(data.get('completed', []))} completed blocks")
                    return data
            except Exception as e:
                print(f"Error loading progress: {e}")
        return {'completed': [], 'total_questions': 0}
    
    def save_progress_state(self, zakon_index, block_index):
        """Save that we completed this zakon/block combination"""
        key = f"{zakon_index}_{block_index}"
        if key not in self.progress['completed']:
            self.progress['completed'].append(key)
            self.progress['total_questions'] = len(self.all_questions)
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def is_completed(self, zakon_index, block_index):
        """Check if this zakon/block combination was already processed"""
        key = f"{zakon_index}_{block_index}"
        return key in self.progress['completed']
        
    def setup_driver(self, headless):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        
    def click_element(self, element, timeout=10):
        """Helper function to click element with wait"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element)
            )
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Error clicking element: {e}")
            return False
            
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Wait for element to be present"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
        except Exception as e:
            print(f"Element not found {selector}: {e}")
            return None

    def extract_questions_from_javascript(self):
        """Extract questions from JavaScript testobj variable"""
        try:
            testobj_script = """
            if (typeof testobj !== 'undefined') {
                return JSON.stringify(testobj);
            } else {
                var scripts = document.getElementsByTagName('script');
                for (var i = 0; i < scripts.length; i++) {
                    var scriptContent = scripts[i].textContent;
                    if (scriptContent.includes('testobj = {')) {
                        var match = scriptContent.match(/testobj\\s*=\\s*({[\\s\\S]*?});/);
                        if (match) {
                            return match[1];
                        }
                    }
                }
                return null;
            }
            """
            
            result = self.driver.execute_script(testobj_script)
            if result:
                testobj = json.loads(result)
                return self.parse_testobj(testobj)
            return []
        except Exception as e:
            print(f"Error extracting questions from JS: {e}")
            return []

    def parse_testobj(self, testobj):
        """Parse testobj structure and extract questions"""
        questions = []
        
        if 'questions' in testobj:
            for theme_id, theme_questions in testobj['questions'].items():
                theme_name = testobj.get('zakon_names', {}).get(theme_id, f"Theme {theme_id}")
                
                for i, question_data in enumerate(theme_questions):
                    question_obj = {
                        'theme_id': theme_id,
                        'theme_name': theme_name,
                        'question_number': i + 1,
                        'question': question_data.get('question', ''),
                        'answers': {},
                        'correct_answer': None,
                        'article': question_data.get('statya', '')
                    }
                    
                    for key, value in question_data.items():
                        if key.startswith('reply'):
                            answer_num = key.replace('reply', '')
                            question_obj['answers'][answer_num] = value
                    
                    correct = question_data.get('correctly')
                    if correct and str(correct) in question_obj['answers']:
                        question_obj['correct_answer'] = str(correct)
                        question_obj['correct_answer_text'] = question_obj['answers'].get(str(correct), '')
                    
                    questions.append(question_obj)
        
        return questions

    def navigate_to_start(self):
        """Navigate to main page and click Program 2"""
        print("Loading main page...")
        self.driver.get('https://findh.org/743-onlayn-testirovanie-na-gosudarstvennuyu-sluzhbu-rk.html')
        time.sleep(3)
        
        print("Navigating to Program 2...")
        program2_element = self.wait_for_element('div.button-table[data-subject="prog2"]')
        if program2_element and self.click_element(program2_element):
            self.wait_for_element('div.window-zakon-choice')
            time.sleep(2)
            return True
        return False

    def get_zakon_info(self, index):
        """Get zakon element by index"""
        try:
            zakons = self.driver.find_elements(By.CSS_SELECTOR, 'div.but-zakons-table[data-zakon-num]')
            if index >= len(zakons):
                return None, None, None
            
            zakon_element = zakons[index]
            zakon_name = zakon_element.find_element(By.CLASS_NAME, 'but-zakons-text').text
            zakon_num = zakon_element.get_attribute('data-zakon-num')
            
            return zakon_element, zakon_name, zakon_num
        except Exception as e:
            print(f"Error getting zakon info: {e}")
            return None, None, None

    def get_block_info(self, index):
        """Get block element by index"""
        try:
            blocks = self.driver.find_elements(By.CSS_SELECTOR, 'div.but-blocks-table[data-block-num]')
            if index >= len(blocks):
                return None, None, None
            
            block_element = blocks[index]
            block_name = block_element.find_element(By.CLASS_NAME, 'but-blocks-text').text
            block_num = block_element.get_attribute('data-block-num')
            
            return block_element, block_name, block_num
        except Exception as e:
            print(f"Error getting block info: {e}")
            return None, None, None

    def get_counts(self):
        """Get total zakons and blocks count"""
        try:
            zakons = self.driver.find_elements(By.CSS_SELECTOR, 'div.but-zakons-table[data-zakon-num]')
            return len(zakons)
        except:
            return 0

    def process_single_block(self, zakon_index, block_index):
        """Process a single zakon/block combination from scratch"""
        
        # Check if already completed
        if self.is_completed(zakon_index, block_index):
            print(f"Block {zakon_index}_{block_index} already completed, skipping...")
            return True
        
        print(f"\n{'='*80}")
        print(f"Processing Zakon {zakon_index + 1}, Block {block_index + 1}")
        print(f"{'='*80}")
        
        # Navigate to start
        if not self.navigate_to_start():
            print("Failed to navigate to start")
            return False
        
        # Click zakon
        zakon_element, zakon_name, zakon_num = self.get_zakon_info(zakon_index)
        if not zakon_element:
            print(f"Failed to get zakon {zakon_index + 1}")
            return False
        
        print(f"Zakon: {zakon_name}")
        if not self.click_element(zakon_element):
            print(f"Failed to click zakon {zakon_index + 1}")
            return False
        
        time.sleep(2)
        self.wait_for_element('div.window-block-choice')
        
        # Click block
        block_element, block_name, block_num = self.get_block_info(block_index)
        if not block_element:
            print(f"Failed to get block {block_index + 1}")
            return False
        
        print(f"Block: {block_name}")
        if not self.click_element(block_element):
            print(f"Failed to click block {block_index + 1}")
            return False
        
        time.sleep(2)
        
        # Start quiz
        print("Starting quiz...")
        quiz_button = self.wait_for_element('div.but-blocks-block-testing-table')
        if not quiz_button or not self.click_element(quiz_button):
            print("Failed to start quiz")
            return False
        
        time.sleep(3)
        
        # Extract questions
        print("Extracting questions...")
        questions = self.extract_questions_from_javascript()
        
        if questions:
            self.all_questions.extend(questions)
            print(f"✓ Extracted {len(questions)} questions")
            print(f"✓ Total questions so far: {len(self.all_questions)}")
            
            # Mark as completed
            self.save_progress_state(zakon_index, block_index)
            self.save_questions()
            return True
        else:
            print("✗ No questions extracted")
            return False

    def parse_all_questions(self):
        """Main method to parse all questions from the site"""
        try:
            # First, get total counts
            if not self.navigate_to_start():
                print("Failed initial navigation")
                return
            
            total_zakons = self.get_counts()
            print(f"\nFound {total_zakons} zakons")
            
            # Get block counts for each zakon
            zakon_blocks = {}
            for z_idx in range(total_zakons):
                if not self.navigate_to_start():
                    continue
                
                zakon_element, zakon_name, _ = self.get_zakon_info(z_idx)
                if zakon_element and self.click_element(zakon_element):
                    time.sleep(2)
                    blocks = self.driver.find_elements(By.CSS_SELECTOR, 'div.but-blocks-table[data-block-num]')
                    zakon_blocks[z_idx] = len(blocks)
                    print(f"Zakon {z_idx + 1} ({zakon_name}): {len(blocks)} blocks")
            
            print(f"\n{'='*80}")
            print(f"Starting to process all blocks...")
            print(f"{'='*80}\n")
            
            # Process each zakon/block combination
            for zakon_index in range(total_zakons):
                num_blocks = zakon_blocks.get(zakon_index, 0)
                
                for block_index in range(num_blocks):
                    success = self.process_single_block(zakon_index, block_index)
                    
                    if not success:
                        print(f"Failed to process zakon {zakon_index + 1}, block {block_index + 1}")
                    
                    # Small delay between blocks
                    time.sleep(2)
            
            print(f"\n{'='*80}")
            print(f"COMPLETED: Total questions extracted: {len(self.all_questions)}")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"Error during parsing: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.save_final_results()

    def save_questions(self):
        """Quick save of questions"""
        try:
            with open('questions_progress.json', 'w', encoding='utf-8') as f:
                json.dump(self.all_questions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving questions: {e}")

    def save_final_results(self):
        """Save final results to multiple formats"""
        if not self.all_questions:
            print("No questions to save")
            return

        # Save as JSON
        with open('all_questions.json', 'w', encoding='utf-8') as f:
            json.dump(self.all_questions, f, ensure_ascii=False, indent=2)

        # Save as readable text
        with open('all_questions.txt', 'w', encoding='utf-8') as f:
            for i, q in enumerate(self.all_questions, 1):
                f.write(f"Question {i}:\n")
                f.write(f"Theme: {q['theme_name']}\n")
                f.write(f"Question: {q['question']}\n")
                f.write("Answers:\n")
                for ans_num, ans_text in q['answers'].items():
                    marker = " ✓" if ans_num == q['correct_answer'] else ""
                    f.write(f"  {ans_num}) {ans_text}{marker}\n")
                f.write(f"Article: {q['article']}\n")
                f.write("-" * 80 + "\n\n")

        # Save as CSV
        import csv
        with open('all_questions.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Theme', 'Question', 'Answer1', 'Answer2', 'Answer3', 'Answer4', 'Correct Answer', 'Article'])
            
            for q in self.all_questions:
                answers = [q['answers'].get(str(i), '') for i in range(1, 5)]
                writer.writerow([
                    q['theme_name'],
                    q['question'],
                    *answers,
                    q['correct_answer'],
                    q['article']
                ])

        print(f"\nResults saved to:")
        print("- all_questions.json (structured data)")
        print("- all_questions.txt (readable format)")
        print("- all_questions.csv (spreadsheet format)")
        print("- parsing_progress.json (progress tracking)")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def main():
    parser = TestParser(headless=False)
    try:
        parser.parse_all_questions()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        print(f"Progress saved. {len(parser.all_questions)} questions extracted so far.")
        print("Run the script again to continue from where you left off.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        parser.close()

if __name__ == "__main__":
    main()
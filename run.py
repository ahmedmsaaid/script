import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import os
import pyperclip
from PIL import Image
import io
import win32clipboard
from io import BytesIO
import random

class FacebookAutomationGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Facebook Group Automation")
        self.window.geometry("800x600")
        
        self.is_running = False
        self.delay_between_posts = tk.StringVar(value="10")
        self.images_folder = tk.StringVar()
        self.add_profile_link = tk.BooleanVar(value=False)
        self.driver = None
        
        # إضافة متغيرات لعرض التقدم
        self.current_cookie = tk.StringVar(value="0/0")
        self.current_group = tk.StringVar(value="0/0")
        
        self.create_gui()
        
    def create_gui(self):
        input_frame = ttk.Frame(self.window, padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # إضافة إطار لعرض التقدم
        progress_frame = ttk.LabelFrame(input_frame, text="حالة التقدم", padding="5")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # عرض رقم الكوكيز الحالي
        cookie_progress_frame = ttk.Frame(progress_frame)
        cookie_progress_frame.pack(fill=tk.X, pady=2)
        ttk.Label(cookie_progress_frame, text="الكوكيز الحالي:").pack(side=tk.LEFT)
        ttk.Label(cookie_progress_frame, textvariable=self.current_cookie).pack(side=tk.LEFT, padx=(5, 0))
        
        # عرض رقم المجموعة الحالية
        group_progress_frame = ttk.Frame(progress_frame)
        group_progress_frame.pack(fill=tk.X, pady=2)
        ttk.Label(group_progress_frame, text="المجموعة الحالية:").pack(side=tk.LEFT)
        ttk.Label(group_progress_frame, textvariable=self.current_group).pack(side=tk.LEFT, padx=(5, 0))
        
        # باقي عناصر الواجهة
        ttk.Label(input_frame, text="الكوكيز (كل كوكيز في سطر منفصل):").pack(anchor=tk.W)
        self.cookie_text = scrolledtext.ScrolledText(input_frame, height=4)
        self.cookie_text.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="روابط المجموعات (رابط واحد في كل سطر):").pack(anchor=tk.W)
        self.groups_text = scrolledtext.ScrolledText(input_frame, height=5)
        self.groups_text.pack(fill=tk.X, pady=(0, 10))
        
        # Add checkbox for profile link
        ttk.Checkbutton(input_frame, text="إضافة رابط الملف الشخصي للمجموعات", 
                       variable=self.add_profile_link).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(input_frame, text="نصوص المنشورات (افصل بين المنشورات بعلامة &&):").pack(anchor=tk.W)
        self.posts_text = scrolledtext.ScrolledText(input_frame, height=5)
        self.posts_text.pack(fill=tk.X, pady=(0, 10))
        
        images_frame = ttk.Frame(input_frame)
        images_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(images_frame, text="مجلد الصور:").pack(side=tk.LEFT)
        ttk.Entry(images_frame, textvariable=self.images_folder, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(images_frame, text="اختيار المجلد", command=self.select_images_folder).pack(side=tk.LEFT)
        
        delay_frame = ttk.Frame(input_frame)
        delay_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(delay_frame, text="الفترة بين المنشورات (بالثواني):").pack(side=tk.LEFT)
        ttk.Entry(delay_frame, textvariable=self.delay_between_posts, width=10).pack(side=tk.LEFT, padx=5)
        
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=10)
        self.start_button = ttk.Button(button_frame, text="بدء النشر", command=self.start_automation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="إيقاف", command=self.stop_automation).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(input_frame, text="جاهز للبدء")
        self.status_label.pack(pady=10)
        
        self.progress = ttk.Progressbar(input_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="سجل العمليات:").pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(input_frame, height=6)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def select_images_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.images_folder.set(folder)

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.window.update_idletasks()

    def create_driver(self):
        try:
            extension_path = "cooke.crx"
            if not os.path.exists(extension_path):
                raise FileNotFoundError("ملف الإضافة cooke.crx غير موجود")
                
            edge_options = Options()
            edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            edge_options.add_extension(extension_path)
            edge_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.clipboard": 1
            })
            
            service = Service("msedgedriver.exe")
            if not os.path.exists("msedgedriver.exe"):
                raise FileNotFoundError("ملف msedgedriver.exe غير موجود")
                
            driver = webdriver.Edge(service=service, options=edge_options)
            driver.implicitly_wait(5)
            return driver
        except Exception as e:
            raise Exception(f"خطأ في إنشاء المتصفح: {str(e)}")
    def clic_empty_space(self,driver):
        try:
            actions = ActionChains(driver)

                # تحريك الماوس لمكان فارغ والنقر
            actions.move_to_element(driver.find_element(By.TAG_NAME, "body"))
            actions.move_by_offset(100, 100)
            actions.click()
            actions.perform()
            
           

            
            time.sleep(1)
        finally:
            self.log("تم النقر في مكان فارغ") 
         
    def click_close_button(self, driver):
        try:
            wait = WebDriverWait(driver, 5)
            close_button_selectors = [
                "//div[@aria-label='Close']",
                "//div[@role='button']//div[text()='Close']", 
                "//span[text()='Close']",
                "//div[contains(@aria-label, 'Close')]"
            ]
            
            for selector in close_button_selectors:
                try:
                    # البحث عن جميع الأزرار المطابقة
                    close_buttons = driver.find_elements(By.XPATH, selector)
                    if close_buttons:
                        # اختيار آخر زر في القائمة
                        last_button = close_buttons[-1]
                        # التأكد من أن الزر قابل للضغط
                        wait.until(EC.element_to_be_clickable((By.XPATH, f"({selector})[{len(close_buttons)}]")))
                        driver.execute_script("arguments[0].click();", last_button)
                        time.sleep(1)
                        self.log("تم الضغط على آخر زر إغلاق")
                        return True
                except:
                    continue
                    
            return False
        except Exception as e:
            self.log(f"خطأ في الضغط على زر الإغلاق: {e}")
            return False         
    def import_cookie(self, driver, cookie):
        try:
            driver.get('chrome-extension://gndjmilpnhjeefkfgggomjggicphnojj/popup.html')
            time.sleep(2)
            
            wait = WebDriverWait(driver, 5)
            result_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cookieresult')))
            result_field.clear()
            result_field.send_keys(cookie)
            
            import_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#btnImportCookie')))
            import_button.click()
            time.sleep(3)
            
            # التحقق من نجاح استيراد الكوكيز
            driver.get('https://www.facebook.com')
            time.sleep(1.5)
            if 'login' in driver.current_url.lower():
                raise Exception("فشل تسجيل الدخول باستخدام الكوكيز")
                
        except Exception as e:
            raise Exception(f"خطأ في استيراد الكوكيز: {str(e)}")
    def find_post_button(self, driver, wait):
        """Try to find the post button with multiple attempts"""
        post_button_selectors = [
            "//span[contains(text(), \"What's on your mind?\")]",
            "//div[contains(text(), \"What's on your mind?\")]",
            "//span[contains(text(), 'Write something...')]",
            "//div[@role='button']//span[contains(text(), 'Write something')]",
        ]
        
        max_attempts = 3
        for attempt in range(max_attempts):
            for selector in post_button_selectors:
                try:
                    post_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post_button)
                    time.sleep(1)
                    post_button.click()
                    return True
                except:
                    continue
                    
            if attempt < max_attempts - 1:
                # If button not found, click empty space and try again
                self.clic_empty_space(driver)
                time.sleep(2)
                
        return False

    def create_post(self, driver, group_link, post_content, image_path):
        try:
            driver.get(group_link)
            wait = WebDriverWait(driver, 10)  # Increased wait time
            
            # Try to find post button with multiple attempts
            if not self.find_post_button(driver, wait):
                raise Exception("لم يتم العثور على زر النشر بعد عدة محاولات")

            time.sleep(2)

            # Find text box
            text_box_selectors = [
                "//div[contains(@aria-label,  \"What's on your mind?\")]",
                "//div[@aria-label='Create a public post…']",
            ]

            text_box = None
            for selector in text_box_selectors:
                try:
                    text_box = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    break
                except:
                    continue

            if not text_box:
                raise Exception("لم يتم العثور على مربع النص")

            time.sleep(2)

            # البحث عن مربع النص وإدخال المحتوى
            text_box_selectors = [
                "//div[contains(@aria-label,  \"What's on your mind?\")]",
                "//div[@aria-label='Create a public post…']",
               
            ]

            text_box = None
            for selector in text_box_selectors:
                try:
                    text_box = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    break
                except:
                    continue

            if not text_box:
                raise Exception("لم يتم العثور على مربع النص")

            # إدخال النص والصورة
            self.paste_content(driver, text_box, post_content, image_path)

            # نشر المحتوى
            return self.submit_post(driver)

        except Exception as e:
            raise Exception(f"خطأ في إنشاء المنشور: {str(e)}")

    def paste_content(self, driver, text_box, post_content, image_path):
        try:
            # إدخال النص
            pyperclip.copy(post_content)
            text_box.click()
            time.sleep(0.5)
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(1)

            # إدخال الصورة
            self.send_to_clipboard(image_path)
            time.sleep(1)
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)

        except Exception as e:
            raise Exception(f"خطأ في إدخال المحتوى: {str(e)}")

    def submit_post(self, driver):
        post_selectors = [
            "//div[text()='Post']",
            "//span[text()='Post']",
            "//div[@aria-label='Post']",
            "//div[@role='button']//div[text()='Post']"
        ]
        
        wait = WebDriverWait(driver, 5)
        is_posted = False  # متغير للتحقق من نجاح النشر
        
        for _ in range(3):  # ثلاث محاولات للنشر
            if is_posted:  # لو تم النشر بنجاح نخرج من الحلقة
                break
                
            for selector in post_selectors:
                try:
                    # محاولة الضغط على زر النشر
                    post_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    driver.execute_script("arguments[0].click();", post_button)
                    self.log("تم الضغط على زر النشر")
                    
                    # انتظار ثانيتين
                    time.sleep(2)
                    
                    # التحقق من وجود "Not now"
                    not_now = driver.find_elements(By.XPATH, "//*[contains(text(), 'Not now')]")
                    if not_now:
                        if self.click_close_button(driver):
                            self.log("تم العثور على Not now وتم الإغلاق")
                        continue
                    
                    # التحقق من علامة التحميل
                    loading = driver.find_elements(By.XPATH, "//div[@role='progressbar']")
                    if loading:
                        self.log("جاري النشر...")
                        time.sleep(3)  # انتظار اكتمال النشر
                        is_posted = True  # تعيين المتغير إلى True عند نجاح النشر
                        break  # الخروج من حلقة السيليكتورز
                    
                except Exception as e:
                   
                    continue
            
            if not is_posted:
                time.sleep(1)
        
        if is_posted:
            self.log("تم النشر بنجاح")
            return True
        else:
            self.log("فشل النشر بعد عدة محاولات")
            return False  # بدلاً من رفع Exception نعيد False
    def send_to_clipboard(self, image_path):
        try:
            image = Image.open(image_path)
            output = BytesIO()
            image.convert('RGB').save(output, 'BMP')
            data = output.getvalue()[14:]
            output.close()
            
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        except Exception as e:
            raise Exception(f"خطأ في نسخ الصورة إلى الحافظة: {str(e)}")

        
    def validate_inputs(self):
        cookies = [c.strip() for c in self.cookie_text.get("1.0", tk.END).splitlines() if c.strip()]
        groups = [g.strip() for g in self.groups_text.get("1.0", tk.END).splitlines() if g.strip()]
        
        # Add profile link to groups if checkbox is checked
        if self.add_profile_link.get():
            groups.append("https://www.facebook.com/me/")
            
        posts_text = self.posts_text.get("1.0", tk.END).strip()
        posts = [p.strip() for p in posts_text.split('&&') if p.strip()]
        images_folder = self.images_folder.get()
        
        if not cookies:
            raise ValueError("الرجاء إدخال كوكيز واحد على الأقل")
            
        if not groups:
            raise ValueError("الرجاء إدخال رابط مجموعة واحد على الأقل")
            
        if not posts:
            raise ValueError("الرجاء إدخال نص منشور واحد على الأقل")
            
        if not os.path.isdir(images_folder):
            raise ValueError("الرجاء اختيار مجلد صور صحيح")
            
        image_files = [f for f in os.listdir(images_folder) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if not image_files:
            raise ValueError("لم يتم العثور على صور في المجلد المحدد")
            
        try:
            delay = int(self.delay_between_posts.get())
            if delay < 5:
                raise ValueError("الفترة بين المنشورات يجب أن تكون 5 ثواني على الأقل")
        except ValueError:
            raise ValueError("الرجاء إدخال رقم صحيح للفترة بين المنشورات")
            
        return cookies, groups, posts, image_files, images_folder, delay

    def distribute_images(self, image_files, cookies, posts):
        """توزيع الصور على الحسابات والمنشورات"""
        images_per_account = len(posts)  # عدد الصور المطلوبة لكل حساب
        distributed_images = []
        
        # نسخ قائمة الصور لتجنب تعديل القائمة الأصلية
        available_images = image_files.copy()
        
        for _ in cookies:
            account_images = []
            
            # محاولة أخذ العدد المطلوب من الصور
            for _ in range(images_per_account):
                if available_images:
                    # إذا كانت هناك صور متاحة، نأخذ واحدة
                    image = available_images.pop(0)
                else:
                    # إذا نفدت الصور، نختار صورة عشوائية من القائمة الأصلية
                    image = random.choice(image_files)
                account_images.append(image)
            
            distributed_images.append(account_images)
            
        return distributed_images

    def run_automation(self, cookies, groups, posts, image_files, images_folder, delay):
        self.status_label.config(text="جاري التشغيل...")
        total_posts = len(groups) * len(posts) * len(cookies)
        self.progress['maximum'] = total_posts
        progress_count = 0
        
        # تحديث العدادات الإجمالية
        self.current_cookie.set(f"0/{len(cookies)}")
        self.current_group.set(f"0/{len(groups)}")
        
        # توزيع الصور على الحسابات
        distributed_images = self.distribute_images(image_files, cookies, posts)
        
        for cookie_index, (cookie, account_images) in enumerate(zip(cookies, distributed_images), 1):
            if not self.is_running:
                break
                
            # تحديث عداد الكوكيز
            self.current_cookie.set(f"{cookie_index}/{len(cookies)}")
            self.log(f"\nجاري استخدام الكوكيز رقم {cookie_index}")
            
            try:
                self.driver = self.create_driver()
                self.import_cookie(self.driver, cookie)
                
                for group_index, group_link in enumerate(groups, 1):
                    if not self.is_running:
                        break
                    
                    # تحديث عداد المجموعات
                    self.current_group.set(f"{group_index}/{len(groups)}")
                    self.log(f"\nجاري النشر في المجموعة: {group_link}")
                    
                    # استخدام صورة مختلفة مع كل منشور
                    for post_index, (post_content, image_file) in enumerate(zip(posts, account_images), 1):
                        if not self.is_running:
                            break
                            
                        try:
                            image_path = os.path.abspath(os.path.join(images_folder, image_file))
                            self.log(f"جاري نشر المنشور رقم {post_index} مع الصورة: {image_file}")
                            
                            self.create_post(self.driver, group_link, post_content, image_path)
                            progress_count += 1
                            self.progress['value'] = progress_count
                            self.window.update_idletasks()
                            
                            time.sleep(delay)
                            
                        except Exception as e:
                            self.log(f"خطأ في نشر المحتوى: {str(e)}")
                            continue
                
                if self.driver:
                    self.driver.quit()
                    self.driver = None
                
            except Exception as e:
                self.log(f"خطأ في استخدام الكوكيز رقم {cookie_index}: {str(e)}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                continue
        
        self.is_running = False
        self.start_button.state(['!disabled'])
        self.status_label.config(text="تم الانتهاء")
        self.log("تم الانتهاء من العملية")
        # إعادة تعيين العدادات عند الانتهاء
        self.current_cookie.set("0/0")
        self.current_group.set("0/0")

    
    def start_automation(self):
        if self.is_running:
            return
            
        try:
            cookies, groups, post_content, image_files, images_folder, delay = self.validate_inputs()
            
            self.is_running = True
            self.start_button.state(['disabled'])
            
            threading.Thread(target=self.run_automation, 
                           args=(cookies, groups, post_content, image_files, images_folder, delay), 
                           daemon=True).start()
                           
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def stop_automation(self):
            if not self.is_running:
                return
                
            self.is_running = False
            self.log("جاري إيقاف العملية...")
            self.status_label.config(text="تم الإيقاف")
            
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                
            self.start_button.state(['!disabled'])
            # إعادة تعيين العدادات عند الإيقاف
            self.current_cookie.set("0/0")
            self.current_group.set("0/0")
    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
        
    def on_closing(self):
        if self.is_running:
            if messagebox.askokcancel("تأكيد", "هل تريد إيقاف العملية وإغلاق البرنامج؟"):
                self.stop_automation()
                self.window.destroy()
        else:
            self.window.destroy()

if __name__ == "__main__":
    app = FacebookAutomationGUI()
    app.run()                            
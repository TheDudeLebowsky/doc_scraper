from os import path
import base64
from selenium.common.exceptions import WebDriverException, NoSuchElementException

class PDFGenerator:
    def __init__(self, driver, output_pdf_dir, output_pdf_file):
        self.driver = driver
        self.output_pdf_dir = output_pdf_dir
        self.output_pdf_file = output_pdf_file

    def save_as_pdf(self):
        try:
            output_path = path.join(self.output_pdf_dir, self.output_pdf_file)
            main_content = self.driver.execute_script("return document.querySelector('main')?.outerHTML;")
            if main_content is None:
                raise ValueError("No 'main' element found in the document.")

            escaped_main_content = main_content.replace('`', '\\`').replace('${', '\\${')
            self.driver.execute_script("window.tempContent = arguments[0];", escaped_main_content)
            self.driver.execute_script("document.body.innerHTML = window.tempContent;")

            print_params = {
                "landscape": False,
                "displayHeaderFooter": False,
                "printBackground": True,
                "preferCSSPageSize": True,
                "scale": 0.5
            }
            result = self.driver.execute_cdp_cmd("Page.printToPDF", print_params)
            if result.get("data") is None:
                raise ValueError("Failed to generate PDF data.")

            with open(output_path, "wb") as f:
                f.write(base64.b64decode(result["data"]))
            print("PDF successfully saved to:", output_path)

        except (WebDriverException, NoSuchElementException, ValueError) as e:
            print(f"Error during PDF creation: {e}")
        finally:
            # Optionally, reset the document body or handle other clean-up if necessary
            self.driver.execute_script("document.body.innerHTML = '';")  # Resetting as an example

# **SmartBookmarks**: A Personal Bookmark Management System

**SmartBookmarks** is an advanced, feature-rich bookmark management system built with **Django**. It is designed to provide users with a simple yet powerful tool to save, organize, and search for bookmarks across categories, files, and URLs. The system tracks bookmarks’ view counts, allows users to organize them into categories, and uses semantic search powered by machine learning embeddings for intelligent results.

This system is tailored for **personal use** with advanced search, analytics, and file handling.

---

## **Table of Contents**

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Tech Stack](#tech-stack)
4. [Installation Guide](#installation-guide)
5. [Configuration](#configuration)
6. [Usage](#usage)

   1. [Add a Bookmark](#add-a-bookmark)
   2. [Search Bookmarks](#search-bookmarks)
   3. [View Bookmarks](#view-bookmarks)
   4. [Delete Bookmarks](#delete-bookmarks)
7. [Search Functionality](#search-functionality)
8. [Analytics & Stats](#analytics--stats)
9. [Bookmark Statistics](#bookmark-statistics)
10. [Folder Structure](#folder-structure)
11. [Development and Contribution](#development-and-contribution)
12. [Troubleshooting](#troubleshooting)
13. [Testing](#testing)
14. [Deployment](#deployment)
15. [License](#license)

---

## **Overview**

**SmartBookmarks** offers a seamless, intelligent, and organized experience for managing your bookmarks. It allows you to store bookmarks for both URLs and files (such as PDFs and DOCX), track them, categorize them, and perform advanced search operations using **semantic search** techniques. It uses **Sentence-Transformers** for embedding-based search and **FAISS** for efficient search over high-dimensional data.

It also provides useful **analytics** by tracking how many times each bookmark has been viewed and showcasing popular bookmarks based on view count.

---

## **Key Features**

### **Bookmark Management**

* **Save Bookmarks**: Save URLs and files (PDFs, DOCX) with metadata such as title, description, and category.
* **Categorize Bookmarks**: Add categories to organize your bookmarks effectively.
* **Edit Bookmarks**: Modify bookmark metadata like title, description, and files.
* **Delete Bookmarks**: Remove unwanted bookmarks from the system permanently.
* **Attach Files**: Upload multiple files per bookmark and associate them for better organization.

### **Search Functionality**

* **Semantic Search**: Use machine learning embeddings to search bookmarks based on their semantic meaning, not just keywords.
* **Text Extraction from Files**: Automatically extract text from PDF and DOCX files to make them searchable.
* **Search History**: Track recent searches for easier access to previously searched items.

### **Analytics & Stats**

* **View Count**: Tracks the number of times a bookmark has been viewed.
* **Popular Bookmarks**: Displays bookmarks sorted by view count to highlight the most popular ones.
* **Bookmark Stats**: Provides insights like the total number of bookmarks, bookmarks per category, etc.

---

## **Tech Stack**

The application is built with the following technologies:

* **Backend**: Django (Web Framework)
* **Frontend**: HTML, CSS, JavaScript (Bootstrap for styling)
* **Database**: SQLite (default, can be swapped with PostgreSQL)
* **Search Engine**: **FAISS** for vector similarity search and **Sentence-Transformers** for generating embeddings.
* **Text Extraction**: **pdfminer.six** for PDFs and **python-docx** for DOCX.
* **Machine Learning**: **Hugging Face Transformers** for zero-shot classification and tagging.

---

## **Installation Guide**

Follow these steps to get **SmartBookmarks** running locally on your machine.

### **Step 1: Clone the Repository**

Clone the project from GitHub:

```bash
git clone https://github.com/alamin72b/SmartBookmarks.git
cd SmartBookmarks
```

### **Step 2: Set Up Virtual Environment**

Create and activate a Python virtual environment:

#### For Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### **Step 3: Install Dependencies**

Install all necessary dependencies by running:

```bash
pip install -r requirements.txt
```

Install any missing libraries manually if needed:

```bash
pip install pdfminer.six python-docx sentence-transformers transformers faiss-cpu
```

### **Step 4: Set Up Database**

Run migrations to set up your database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### **Step 5: Create a Superuser**

Create a superuser account to access the Django admin interface:

```bash
python manage.py createsuperuser
```

### **Step 6: Run the Development Server**

Start the Django development server:

```bash
python manage.py runserver
```

Your app will be available at `http://127.0.0.1:8000/`.

---

## **Configuration**

Ensure that the **FAISS index** and **vector map** files are correctly configured in `settings.py`:

```python
BASE_DATA_DIR = Path(getattr(settings, "BASE_DATA_DIR", settings.BASE_DIR))
VECTOR_MAP_FILE = getattr(settings, "VECTOR_MAP_FILE", BASE_DATA_DIR / "faiss_vector_map.json")
FAISS_INDEX_FILE = getattr(settings, "FAISS_INDEX_FILE", BASE_DATA_DIR / "faiss_index.bin")
```

---

## **Usage**

Once the application is up and running, here’s how to interact with it:

### **Add a Bookmark**

1. Navigate to the homepage.
2. Click on the "Add Bookmark" button.
3. Provide the title, description, and category.
4. Attach any relevant files (PDF, DOCX).
5. Click "Save" to store the bookmark.

### **Search Bookmarks**

Use the search bar to search for bookmarks. The results will be based on the **title**, **description**, and **extracted text** (from attached files). The search is powered by **semantic search** and **FAISS** to ensure relevant results.

### **View Bookmarks**

Click on any bookmark to view detailed information such as its title, description, URL, and attached files.

### **Delete Bookmarks**

On the bookmark detail page, click the "Delete Bookmark" button to remove the bookmark permanently.

---

## **Search Functionality**

The search functionality is powered by **semantic search** with **Sentence-Transformers** embeddings. Here's how it works:

1. **Text Input**: The user enters a search query (e.g., a title or description).
2. **Generate Embedding**: The query is converted into an embedding using **Sentence-Transformers**.
3. **FAISS Search**: The generated embedding is used to search for the most similar bookmarks stored in the **FAISS** index.
4. **Results**: The most relevant bookmarks are displayed.

---

## **Analytics & Stats**

### **View Count**

Each time a bookmark's detail page is visited, the view count is incremented by 1. This count is stored in the database and can be used to display popular bookmarks.

### **Popular Bookmarks**

The "Popular Bookmarks" section on the homepage lists bookmarks sorted by view count. These are the bookmarks that have been viewed the most.

### **Bookmark Stats**

The statistics page shows:

* Total number of bookmarks saved.
* Number of bookmarks per category.

---

## **Folder Structure**

The project follows a standard Django structure:

```plaintext
smartbookmarks/
│
├── bookmarks/               # Core app
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates
│   ├── models.py            # Models for Bookmarks, Categories, etc.
│   ├── views.py             # Views to handle requests
│   ├── forms.py             # Forms for input handling
│   ├── utils.py             # Utility functions for text extraction, embedding, etc.
│   ├── urls.py              # URL routing for the app
│
├── manage.py                # Django management script
├── requirements.txt         # List of required Python packages
└── settings.py              # Project settings file
```

---

## **Development and Contribution**

### **Fork the Repository**

1. **Fork** this repository to your GitHub account.
2. Clone your forked repository:

```bash
git clone https://github.com/almain72b/SmartBookmarks.git
cd SmartBookmarks
```

### **Contribute**

To contribute to the project:

1. Create a new branch for your feature:
   `git checkout -b feature-name`
2. Implement your changes and **test** them.
3. Commit your changes:
   `git commit -am 'Add feature'`
4. Push your changes:
   `git push origin feature-name`
5. **Submit a pull request** from your feature branch to the `main` branch.

### **Code Style**

* Follow **PEP 8** for Python code style.
* Use **4 spaces** for indentation.
* Write tests for any new features or changes.

---

## **Troubleshooting**

### **No File Submitted Error**

Ensure that your HTML form includes the correct `enctype="multipart/form-data"` for file uploads:

```html
<form method="POST" enctype="multipart/form-data">
```

---

## **Testing**

To run the tests for this application, use Django’s testing framework.

1. **Run Tests**:

```bash
python manage.py test
```

2. **Test Coverage**: Ensure your changes are well-tested and add new tests where necessary.

---

## **Deployment**

### **Deploy to Production**

This project is ready to be deployed to a production environment. Here are the general steps to deploy to a service like **Heroku** or **DigitalOcean**:

1. **Set Environment Variables**: Configure your production environment variables (e.g., secret keys, database credentials).
2. **Set Up a Production Database**: Use **PostgreSQL** for better performance.
3. **Collect Static Files**: Run `python manage.py collectstatic` to collect all static files in a single location for production.
4. **Set Up WSGI**: Configure **Gunicorn** or **uWSGI** as your WSGI server.

---

## **License**

This project is licensed under the **MIT License**.

---

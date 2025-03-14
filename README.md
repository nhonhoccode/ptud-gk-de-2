# Task Management Application

<div align="center">
  <h2>Developed by</h2>
  <h1>Võ Trọng Nhơn (Maximus)</h1>
  <h3>Student ID: 22658441</h3>
  <hr>
</div>

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Image Optimization](#image-optimization-features)
- [Template Tags](#template-tags)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

This project is a comprehensive task management system built with Django that allows users to organize their tasks by categories and provides optimized image handling for better performance. The application features a modern, responsive UI built with Bootstrap 5.

## Features

### User Authentication System
- User registration, login, and logout functionality
- Profile management with customizable avatars
- Password change capabilities

### Task Management
- Create, read, update, and delete tasks
- Task status tracking (Pending, In Progress, Completed)
- Task completion time monitoring
- Task filtering and organization

### Category System
- Create and manage task categories
- Assign colors and icons to categories
- Filter tasks by category
- Category statistics

### Performance Optimizations
- Image optimization middleware
- Avatar caching system
- Lazy loading for images
- Static file optimization
- Database query caching

### UI/UX Improvements
- Responsive design for all screen sizes
- Modern card-based layout
- Interactive statistics dashboard
- Optimized image loading with placeholders
- Animated transitions

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step-by-Step Installation

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd task-management
   ```

2. **Create a virtual environment**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

5. **Set up the database**
   ```
   python manage.py migrate
   ```

6. **Create a superuser (admin)**
   ```
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

7. **Generate optimized avatar cache (optional but recommended)**
   ```
   python manage.py generate_avatar_cache
   ```

8. **Run the development server**
   ```
   python manage.py runserver
   ```

9. **Access the application**
   Open your browser and navigate to: http://127.0.0.1:8000/

## Usage

After installation, you can:

1. **Register a new account** or log in with your credentials
2. **Create tasks** by clicking the "New Task" button
3. **Organize tasks into categories** for better management
4. **Track your progress** with the interactive dashboard
5. **Update your profile** including customizing your avatar
6. **Filter tasks** by status or category

## Image Optimization Features

This application includes several image optimization features to improve performance:

### 1. Avatar Caching

The application can cache avatar images locally to reduce external API calls:

```
python manage.py generate_avatar_cache
```

Options:
- `--count`: Number of avatars to download (default: 92)
- `--sizes`: Comma-separated list of sizes to generate (default: 38,96,200)
- `--format`: Image format to save as (default: webp)
- `--quality`: Image quality for JPEG/WebP (default: 85)

### 2. Image Optimization

Optimize existing images in the media directory:

```
python manage.py optimize_images
```

Options:
- `--quality`: JPEG/WebP quality (default: 85)
- `--convert`: Convert images to this format (choices: webp, jpeg, none; default: webp)
- `--max-width`: Maximum width for images (default: 1920)
- `--max-height`: Maximum height for images (default: 1080)

### 3. Middleware

The application includes middleware that automatically:
- Adds appropriate cache headers for images
- Adds lazy loading to images below the fold
- Optimizes image delivery

## Template Tags

The application provides custom template tags for optimized image rendering:

### optimized_img

```html
{% load image_tags %}
{% optimized_img src="image.jpg" alt="Description" width=200 height=150 css_class="img-fluid" %}
```

### avatar_img

```html
{% load image_tags %}
{% avatar_img user_profile size="small" css_class="avatar-sm" alt="User Avatar" %}
```

Size options: "small" (38px), "medium" (96px), "large" (200px), or custom integer value

## Project Structure

- `tasks/`: Main application
  - `management/commands/`: Custom management commands for image optimization
  - `middleware.py`: Image optimization middleware
  - `templatetags/`: Custom template tags for image rendering
  - `models.py`: Data models including User Profile, Task, and Category
  - `views.py`: View functions for handling requests
  - `forms.py`: Form definitions for data input
- `templates/`: HTML templates
  - `tasks/`: Application-specific templates
  - `base.html`: Base template with common elements
- `static/`: Static files
  - `img/avatars/`: Cached avatar images
- `media/`: User-uploaded files

## Troubleshooting

If you encounter any issues:

1. **Database migration errors**
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Static files not loading**
   ```
   python manage.py collectstatic
   ```

3. **Missing dependencies**
   Ensure all packages in requirements.txt are installed:
   ```
   pip install -r requirements.txt
   ```

4. **Image optimization errors**
   Make sure Pillow is properly installed:
   ```
   pip install --upgrade Pillow
   ```

## License

MIT License 
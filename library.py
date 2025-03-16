import streamlit as st
import json
import os
import base64
from urllib.parse import urlencode
import streamlit.components.v1 as components

DATA_FILE = "library.json"
PDF_FOLDER = "pdfs/"

if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

def show_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'''
        <div style="width: 100%; min-width: 800px;">
            <iframe src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" 
                    height="1200px" 
                    type="application/pdf"
                    style="border: none;">
            </iframe>
        </div>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

def load_library():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

def save_library(library):
    with open(DATA_FILE, 'w') as file:
        json.dump(library, file, indent=4)

def add_book(title, author, year, genre, pdf_file):
    library = load_library()
    pdf_path = None
    if pdf_file:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file.name)
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())
    
    new_book = {
        "title": title,
        "author": author,
        "year": year,
        "genre": genre,
        "pdf_path": pdf_path
    }
    library.append(new_book)
    save_library(library)
    st.success(f"Book '{title}' added successfully!")

def remove_book(title):
    library = load_library()
    updated_library = [book for book in library if book["title"].lower() != title.lower()]
    
    if len(updated_library) < len(library):
        save_library(updated_library)
        st.success(f"Book '{title}' removed successfully!")
    else:
        st.warning(f"Book '{title}' not found in the library.")

def display_books(search_term=None, search_by=None):
    library = load_library()
    if search_term and search_by:
        library = [book for book in library if search_term.lower() in book.get(search_by, "").lower()]
    
    if library:
        for book in library:
            # Create a unique key for this book's state
            viewer_key = f"show_pdf_{book['title']}"
            if viewer_key not in st.session_state:
                st.session_state[viewer_key] = False

            # Create container for each book
            book_container = st.container()
            with book_container:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"### {book['title']}")
                    st.write(f"by {book['author']} ({book['year']}) - {book['genre']}")
                if book.get("pdf_path"):
                    with col2:
                        with open(book["pdf_path"], "rb") as pdf:
                            st.download_button(
                                label="Download PDF",
                                data=pdf,
                                file_name=os.path.basename(book["pdf_path"])
                            )
                    with col3:
                        if st.button(
                            "Read Book" if not st.session_state[viewer_key] else "Close Book",
                            key=f"read_{book['title']}"
                        ):
                            st.session_state[viewer_key] = not st.session_state[viewer_key]
                
                # Show PDF viewer if state is True
                if st.session_state[viewer_key]:
                    show_pdf(book["pdf_path"])
                
                # Add a separator between books
                st.markdown("---")
    else:
        st.write("No books found in the library.")

def get_shareable_link():
    base_url = "https://your-streamlit-app-url.com"  # Replace with your actual URL when deployed
    if st.button("Generate Shareable Link"):
        share_link = f"{base_url}?shared=true"
        st.code(share_link)
        st.markdown(f"""
        <input type="text" value="{share_link}" id="shareLink" readonly style="width: 100%; padding: 8px;">
        <button onclick="navigator.clipboard.writeText(document.getElementById('shareLink').value)">
            Copy Link
        </button>
        """, unsafe_allow_html=True)

# Main UI
st.title("📚 Library Manager")

# Get the 'shared' parameter from URL
is_shared = st.query_params.get("shared", False)

if is_shared:
    # Shared view mode
    st.header("Shared Library Collection")
    display_books()
else:
    # Normal mode with all features
    menu = st.sidebar.selectbox("Menu", ["Add Book", "View Books", "Search Books", "Remove Book", "Share Library"])

    if menu == "Add Book":
        st.header("Add a New Book")
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.text_input("Year")
        genre = st.text_input("Genre")
        pdf_file = st.file_uploader("Upload Book PDF", type=["pdf"])
        if st.button("Add Book"):
            add_book(title, author, year, genre, pdf_file)

    elif menu == "View Books":
        st.header("Library Collection")
        display_books()

    elif menu == "Search Books":
        st.header("Search Library")
        search_by = st.selectbox("Search by", ["title", "author", "genre", "year"])
        search_term = st.text_input("Enter search term")
        if st.button("Search"):
            display_books(search_term, search_by)

    elif menu == "Remove Book":
        st.header("Remove a Book")
        title = st.text_input("Enter book title to remove")
        if st.button("Remove Book"):
            remove_book(title)

    elif menu == "Share Library":
        st.header("Share Your Library")
        st.write("Generate a shareable link to your library:")
        get_shareable_link()
        st.write("""
        ### Sharing Instructions:
        1. Click the 'Generate Shareable Link' button above
        2. Copy the generated link
        3. Share this link with anyone you want to give access to your library
        4. They will be able to view and read books but cannot modify the library
        """)

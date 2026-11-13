# AI Usage Log — Garuda Dictionary

**Project:** Garuda Prakashan × Rishihood University — Dictionary App Track  
**Date:** November 2026

## 1. AI Tools Used

| Tool | Purpose |
|---|---|
| Google Antigravity | Development assistance, code suggestions, debugging support, and test generation |
| ChatGPT | Project planning, technical guidance, understanding implementation choices, and reviewing functionality |

## 2. Development Approach

The project was developed using Django, SQLite, HTML, CSS, and vanilla JavaScript.

The primary focus was to build a functional dictionary application that supports both Devanagari and Romanised Hindi searches.

I worked on understanding the requirements, structuring the application, reviewing the implementation, and making decisions regarding its functionality and user experience. AI tools were used as development assistance for specific implementation tasks, code suggestions, and debugging.

The project was approached in the following stages:

1. Understanding the assignment requirements and identifying the essential features.
2. Setting up the Django project and designing the database structure.
3. Implementing dictionary search functionality for Devanagari, Romanised Hindi, and English meanings.
4. Developing the frontend using Django templates, HTML, CSS, and JavaScript.
5. Adding autocomplete, word details, filtering, and other interactive features.
6. Testing the application and addressing issues encountered during development.
7. Preparing the documentation and reviewing the overall project structure.

## 3. Areas Where AI Assistance Was Used

AI tools were used selectively throughout development for:

- **Project structure:** Suggestions for organizing Django applications, templates, static files, and backend components.
- **Database design:** Assistance in defining the DictionaryEntry model and its fields.
- **Search implementation:** Suggestions for implementing different search levels, alternate Romanisations, and Unicode normalization.
- **Frontend development:** Assistance with CSS styling, responsive layouts, and Django templates.
- **JavaScript:** Suggestions for autocomplete, keyboard navigation, debouncing, and clipboard functionality.
- **Sample data:** Generation of demonstration dictionary entries for testing the application.
- **Testing:** Assistance in preparing test cases for search functionality, API endpoints, and page responses.
- **Documentation:** Assistance in structuring the README and technical documentation.

AI-generated suggestions were treated as development inputs and were reviewed against the project's requirements.

## 4. Technical and Design Decisions

The following implementation choices were made for the project:

| Decision | Reason |
|---|---|
| Django | Provides a structured backend, ORM, URL routing, and template integration. |
| SQLite | Suitable for a lightweight prototype without additional database setup. |
| Vanilla JavaScript | Keeps the frontend lightweight and avoids unnecessary framework dependencies. |
| Django Templates | Allows backend data to be rendered directly into HTML pages. |
| Alternate Romanisation storage | Supports different spellings of the same word without requiring a complex database structure. |
| Ranked search | Prioritizes exact matches over partial and meaning-based matches. |
| Unicode normalization | Helps handle different Unicode representations of Devanagari text. |
| Demonstration dataset | Allows the application to be tested independently of an external dictionary API. |

These choices were made to keep the application practical, maintainable, and appropriate for the assignment's scope.

## 5. Suggestions Reviewed and Modified

During development, AI-generated suggestions were reviewed based on the requirements and simplicity of the application.

Some implementation approaches were retained because they suited the project, while others required review or further adjustment.

Examples of areas reviewed include:

- Search priority and matching behaviour.
- Handling of alternate Romanised spellings.
- Unicode normalization for Indian-language text.
- Responsive layout and typography.
- Autocomplete behaviour and handling of repeated requests.
- Database fields and relationships.
- Validation of API input.

**Personal modifications:**  
[Add the specific changes you personally made after reviewing and running the application. Include actual examples rather than generic statements.]

## 6. Testing and Verification

The application includes a Django test suite covering the main functionality.

The following test categories were covered:

- Exact Devanagari search.
- Exact Romanised search.
- Case-insensitive matching.
- Alternate Romanisation matching.
- Prefix and partial matching.
- English meaning search.
- Empty and whitespace-only queries.
- Unknown word handling.
- Dictionary entry detail pages.
- API response structure.
- API input validation.
- Unicode normalization.
- Homepage and Explore page responses.
- Part-of-speech filtering.

**Reported automated test result:** 38 out of 38 tests passed after fixing a whitespace-query issue.

The test results should be considered alongside manual browser testing and code review.

Additional manual testing performed:

[Document the actual browser, device, search queries, and interactive features you personally tested.]

## 7. Dictionary Content and Data Sources

The application currently contains 42 demonstration entries.

These entries were used to test the dictionary's search functionality and display structure.

The sample dataset includes commonly used words such as:

- धर्म
- ज्ञान
- कर्म
- योग
- पुस्तक
- शिक्षा
- संस्कृति
- सत्य
- अहिंसा
- विचार

AI assistance was used to generate the initial demonstration content.

The entries have not been independently verified by Garuda Prakashan's editorial team or a qualified linguist. Therefore, the dataset is treated as illustrative rather than an authoritative dictionary.

## 8. My Contribution and Learning

Working on this project helped me understand how a dictionary application can be structured using Django and a lightweight frontend.

Some of the key technical areas explored during development were:

- Connecting Django models with database records.
- Understanding Django views and URL routing.
- Using Django templates to display dynamic data.
- Implementing search logic using Django ORM queries.
- Handling Devanagari Unicode text.
- Connecting frontend JavaScript with backend JSON endpoints.
- Understanding debouncing and asynchronous autocomplete requests.
- Writing automated tests for application functionality.
- Organizing a Django project for maintainability.

I also considered the importance of designing search functionality specifically for Indian-language users, where the same word may be entered using different Romanised spellings.

## 9. Limitations and Future Improvements

The current version is a working prototype. Some areas that could be improved in future versions include:

- Integrating an authorized and editorially verified dictionary dataset.
- Improving transliteration and phonetic search.
- Adding pronunciation and audio support.
- Supporting additional Indian languages.
- Improving semantic search and related-word recommendations.
- Expanding linguistic information and source references.
- Conducting usability testing with actual dictionary users.

## 10. Final Note

AI tools were used as development assistants during this project, particularly for implementation suggestions, code generation, debugging, and test preparation.

The objective was not simply to generate a website, but to understand the requirements and develop a functional prototype that demonstrates how Devanagari and Romanised dictionary search can work together.

The final submission should be understood as a student-developed project with disclosed AI assistance.

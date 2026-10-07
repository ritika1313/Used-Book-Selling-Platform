🎯 Interview-specific answer
Q: How did you handle authentication in your FastAPI application?
"I used API-key based authentication with FastAPI dependency injection. I created a reusable verify_api_key function in auth.py, which validates the X-API-Key header. For protected endpoints like creating or updating books, I use Depends(verify_api_key). If the key is missing or invalid, the request is rejected with an authentication error. This keeps authentication logic separate from the business logic and makes it reusable across multiple endpoints."

बस. इतना enough है.
If interviewer asks: "Which APIs are protected?"
"In my application, operations that modify data, such as creating a book, updating a book, marking it as sold, and registering a user, are protected. Book listing and searching are public."

If interviewer asks: "Why did you use Depends()?"
"Depends() allows FastAPI to automatically execute reusable logic before the endpoint. I used it for authentication so I don't have to repeat the API-key validation code in every protected route."

If interviewer asks: "What happens with an invalid API key?"
"The verify_api_key dependency checks the key, and if it doesn't match, it raises an HTTP 401 error. The actual endpoint logic is not executed."

If interviewer asks: "Why separate authentication into auth.py?"
"It's separation of concerns. auth.py handles authentication, while the route files handle the actual business logic. This makes the code reusable and easier to maintain."

If interviewer asks: "Is your authentication production-ready?"
"It's suitable for this academic project, but for production I would store the secret in environment variables or a secret manager and use proper user authentication and authorization, such as JWT."
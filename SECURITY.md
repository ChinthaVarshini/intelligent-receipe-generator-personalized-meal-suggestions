# Security Configuration Guide

## API Key Security Implementation

### Overview
This document outlines the security measures implemented to protect API keys and sensitive configuration in the Intelligent Recipe Generator application.

## Changes Made

### 1. Removed Hardcoded API Keys from Frontend ✅
**Before:**
```javascript
const API_KEY = 'intelligent-recipe-generator-api-key-2023';
headers: {
  'X-API-Key': 'intelligent-recipe-generator-api-key-2023'
}
```

**After:**
```javascript
// API keys are no longer exposed in client-side code
// Authentication uses JWT tokens instead
```

### 2. Frontend Authentication Strategy
The frontend now uses JWT token-based authentication:
- JWT tokens are obtained during login/registration
- Tokens are stored securely in localStorage
- All authenticated requests include: `Authorization: Bearer <token>`
- No API keys are exposed in the frontend code

### 3. Backend API Key Protection
- API keys remain in backend `.env` file only
- Backend validates API keys for external/test requests
- Frontend requests are validated using JWT tokens
- Cross-origin requests use CORS policies

## Environment Variables

### Backend (.env file)
```bash
API_KEY=your-secure-api-key-here
JWT_SECRET_KEY=your-secret-jwt-key-here
DATABASE_URL=your-database-url
```

**Security Tips:**
- Never commit `.env` file to version control
- Add `.env` to `.gitignore`
- Use strong, unique API keys for production
- Rotate keys periodically
- Use different keys for development and production

### Frontend (.env file - if needed)
```bash
REACT_APP_API_URL=http://localhost:8000
# Never store API keys in frontend .env
```

## JWT Token Security

### Token Generation
- Tokens are issued upon successful login/registration
- Tokens include user ID and expiration time
- Tokens are signed with a secret key

### Token Storage
- Tokens are stored in browser localStorage
- Consider using httpOnly cookies for higher security in production
- Tokens are cleared on logout

### Token Usage
```javascript
const token = localStorage.getItem('token');
const headers = {
  'Authorization': `Bearer ${token}`
};
```

## Best Practices Implemented

### ✅ Frontend
1. No hardcoded API keys in code
2. API keys removed from all components
3. JWT token-based authentication
4. Relative API paths (same-origin requests)
5. Secure header management

### ✅ Backend
1. API key stored in environment variables
2. Sensitive data never logged to console (in production)
3. CORS policy configured for trusted origins
4. JWT secret key in environment variables
5. Token validation on protected routes

## Testing with API Keys

### For Development/Testing
If you need to test external API endpoints, use environment variables:

```python
# backend/.env
API_KEY=test-api-key-for-development
```

### Test Scripts
Test scripts should read API keys from environment:
```python
import os
API_KEY = os.getenv('API_KEY', 'default-key')
```

## Production Deployment

### Before Going to Production:

1. **Generate New API Keys**
   - Create strong, unique keys
   - Use a key management service (AWS Secrets Manager, HashiCorp Vault, etc.)

2. **Update Environment Variables**
   - Set all keys in production environment
   - Use secure secret management

3. **Enable HTTPS**
   - Use SSL/TLS certificates
   - Redirect HTTP to HTTPS

4. **Set Secure CORS**
   ```python
   CORS(app, origins=['https://yourdomain.com'])
   ```

5. **Use HttpOnly Cookies**
   Replace localStorage with secure httpOnly cookies for tokens

6. **Implement Rate Limiting**
   - Protect API endpoints from abuse
   - Use tools like Flask-Limiter

7. **Add Logging & Monitoring**
   - Monitor suspicious activity
   - Alert on failed authentication attempts

## Files Modified

### Frontend Files (API keys removed)
- `src/pages/Login.js`
- `src/pages/Recipes.js`
- `src/pages/Profile.js`
- `src/pages/RecipeDetail.js`
- `src/pages/Ingredients.js` (via Redux slice)
- `src/features/ingredientSlice.js`
- `src/features/recipeSlice.js`

### New Files Created
- `src/utils/api-config.js` - Secure API configuration utility

### Backend Files (Unchanged - already secure)
- `backend/app/main.py` - Already uses environment variables
- `backend/app/config.py` - Reads from environment

## Security Checklist

- [x] Remove hardcoded API keys from frontend
- [x] Remove API keys from GitHub commits
- [x] Use environment variables for sensitive data
- [x] Implement JWT token-based authentication
- [x] Create `.gitignore` entry for `.env` file
- [x] Document security practices
- [ ] Set up HTTPS in production
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular security audits

## References

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Environment Variables & Secrets](https://12factor.net/config)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)

## Questions or Issues?

If you find any security issues, please:
1. Do not commit the issue or expose it publicly
2. Contact the development team privately
3. Provide detailed information about the vulnerability

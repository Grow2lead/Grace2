# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-28

### Added
- Initial release of Health App
- User authentication system with JWT tokens
- Custom user model with extended fields
- Nutrition tracking with foods and meal logs
- Activity tracking and logging
- RESTful API with comprehensive documentation
- Multi-language support (English, Sinhala, Tamil)
- CORS configuration for frontend integration
- Database support for both SQLite and MySQL
- API documentation with Swagger/OpenAPI
- Web interface templates for key features

### Features
- **Authentication**: JWT-based authentication with custom user model
- **Nutrition Module**: CRUD operations for foods and meal logging
- **Activity Module**: CRUD operations for activity tracking
- **API Documentation**: Auto-generated API docs at `/api/docs`
- **Multi-database Support**: SQLite for development, MySQL for production
- **Localization**: Support for multiple languages
- **CORS**: Enabled for cross-origin requests in development

### Technical Details
- Django 5.2.5 framework
- Django REST Framework for API
- JWT authentication with Simple JWT
- MySQL and SQLite database support
- Environment-based configuration
- Comprehensive API filtering and search

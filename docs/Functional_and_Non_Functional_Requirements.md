# AI-Based Crop Irrigation Scheduler Web Application

This web application provides a smart, data-driven solution for crop irrigation scheduling. It leverages a machine learning model to deliver precise, real-time watering recommendations. 
The goal is to optimize water usage, enhance crop yields, and promote sustainable agricultural practices, particularly in regions facing water scarcity.

This system is designed as a decision support tool for farmers, providing AI-generated schedules and actionable recommendations through a simple, user-friendly interface.

---

## **Key Features**

**User Management**: Secure user registration and login.
**Crop & Field Input**: An intuitive interface for farmers to input details about their crops, including type, growth stage, and location[cite: 75, 333].
**Data Integration**: Automatically fetches and processes historical and real-time weather data from external APIS.
It also allows for the input of soil moisture data.
**AI-Powered Scheduling**: Utilizes a machine learning algorithm to analyze environmental data and generate optimal irrigation schedules.
**Dynamic Recommendations**: Provides real-time watering advice that adapts to current environmental conditions.

---

## **Functional Requirements**

These are the specific actions the system must be able to perform.

**User Authentication and Authorization**: The system will securely manage user access, requiring users to log in to view and manage their specific irrigation schedules.

**Crop Data Input**: Farmers must be able to input and save details about their crops, including **crop type**, **growth stage**, and **field location**[cite: 333].
**Historical Weather Data Retrieval**: The application will access and process historical weather data relevant to a user's specified location to inform the prediction model.
**Real-time Weather Data Retrieval**: The system will integrate with live weather APIs to fetch current and forecasted weather conditions (e.g., temperature, humidity, rainfall forecast).
**Soil Moisture Data Processing**: The system must allow for the input or integration of soil moisture data, either from IoT sensors or manual measurements entered by the user.
**Irrigation Schedule Generation**: The core function is to use the machine learning algorithm (initially proposed as CART, with a Random Forest model implemented) to generate optimal irrigation schedules based on all integrated data.
**Real-time Irrigation Recommendation Provision**: The system will provide dynamic watering recommendations (e.g., "Light Irrigation," "Wait") based on up-to-the-minute environmental conditions.
**User Interface Display**: All schedules and recommendations must be presented to the farmer in a clear, intuitive, and actionable format.

---

## **Non-Functional Requirements**

These requirements define the quality attributes and overall performance of the system.

* **Performance**: The web app must generate schedules and provide real-time recommendations with minimal delay to ensure farmers can make timely decisions.Data processing of large datasets should be efficient.
* **Usability**: The user interface must be **intuitive, easy to navigate, and require minimal technical expertise**. Information should be presented clearly and concisely to be easily understood by farmers.
* **Reliability**: The system must be dependable and consistently available, with minimal downtime. The accuracy of the data and the advice provided are crucial for building trust.
**Security**: All user data, especially personal and farm-specific information, must be protected against unauthorized access and security breaches to ensure data privacy[cite: 356].
**Scalability**: The application architecture should be designed to handle a growing number of users, crops, and data sources without a significant drop in performance[cite: 357].
**Maintainability**: The codebase and system architecture must be well-structured and documented to allow for easy modifications, updates, and bug fixes in the future.
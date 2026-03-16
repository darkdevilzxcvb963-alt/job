# Requirements Specification

## 1. Functional Requirements

### 1.1 Candidate Management
- **FR-C1**: The system shall allow candidates to upload resumes in PDF and DOCX formats.
- **FR-C2**: The system shall automatically parse uploaded resumes to extract contact information, skills, and experience.
- **FR-C3**: The system shall generate a summary of the candidate's professional profile using an LLM.
- **FR-C4**: Candidates shall be able to view their matches with available job postings.

### 1.2 Recruiter & Job Management
- **FR-R1**: Recruiters shall be able to post job openings with titles, descriptions, and required skills.
- **FR-R2**: The system shall automatically normalize job titles to standard industry terms.
- **FR-R3**: Recruiters shall be able to view top-matching candidates for their job postings.
- **FR-R4**: Recruiters shall be able to contact candidates directly via phone from the matches view.

### 1.3 Matching System
- **FR-M1**: The system shall compute a matches score based on semantic similarity, skill overlap, and experience.
- **FR-M2**: The system shall provide an LLM-generated explanation for each match score.
- **FR-M3**: Users shall be able to filter and rank matches by score.

### 1.4 Admin Features
- **FR-A1**: Admins shall be able to verify, activate, or deactivate user accounts.
- **FR-A2**: Admins shall be able to approve or reject recruiter companies for verification.
- **FR-A3**: The system shall display real-time statistics on user growth and platform metrics.

## 2. Non-Functional Requirements

### 2.1 Performance
- **NFR-P1**: Backend API startup time should be less than 5 seconds.
- **NFR-P2**: Resume parsing and matching should complete in under 2 seconds per file.
- **NFR-P3**: The system shall support asynchronous processing for large file uploads.

### 2.2 Security
- **NFR-S1**: All user passwords shall be hashed using secure algorithms (BCrypt).
- **NFR-S2**: Authentication shall be handled using JWT tokens with configurable expiry.
- **NFR-S3**: Role-Based Access Control (RBAC) must be enforced for all sensitive endpoints.

### 2.3 Scalability
- **NFR-SC1**: The architecture shall be modular to allow for future replacement of the NLP or LLM components.
- **NFR-SC2**: The system shall support containerization using Docker for easy deployment and scaling.

### 2.4 Usability
- **NFR-U1**: The frontend shall be responsive and accessible on both desktop and mobile devices.
- **NFR-U2**: The Admin Dashboard shall provide a clear, intuitive interface for managing platform health.

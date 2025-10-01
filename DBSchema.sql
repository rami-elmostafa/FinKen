-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.PasswordHistory (
  PasswordHistoryID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  UserID integer NOT NULL,
  PasswordHash character varying NOT NULL,
  DateSet timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT PasswordHistory_pkey PRIMARY KEY (PasswordHistoryID),
  CONSTRAINT fk_password_history_user FOREIGN KEY (UserID) REFERENCES public.Users(UserID)
);

CREATE TABLE public.RegistrationRequests (
  RequestID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  FirstName text NOT NULL,
  LastName text NOT NULL,
  Email text NOT NULL,
  DOB date,
  Address text,
  RequestDate timestamp with time zone NOT NULL DEFAULT now(),
  Status text NOT NULL DEFAULT 'Pending'::text CHECK ("Status" = ANY (ARRAY['Pending'::character varying::text, 'Approved'::character varying::text, 'Rejected'::character varying::text])),
  ReviewedByUserID integer,
  ReviewDate timestamp with time zone,
  CONSTRAINT RegistrationRequests_pkey PRIMARY KEY (RequestID),
  CONSTRAINT fk_reviewed_by_user FOREIGN KEY (ReviewedByUserID) REFERENCES public.Users(UserID)
);

CREATE TABLE public.Roles (
  RoleID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  RoleName character varying NOT NULL UNIQUE,
  CONSTRAINT Roles_pkey PRIMARY KEY (RoleID)
);

CREATE TABLE public.SecurityQuestions (
  QuestionID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  QuestionText character varying NOT NULL UNIQUE,
  CONSTRAINT SecurityQuestions_pkey PRIMARY KEY (QuestionID)
);

CREATE TABLE public.UserSecurityAnswers (
  UserAnswerID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  UserID integer NOT NULL,
  QuestionID integer NOT NULL,
  AnswerHash character varying NOT NULL,
  CONSTRAINT UserSecurityAnswers_pkey PRIMARY KEY (UserAnswerID),
  CONSTRAINT fk_answer_user FOREIGN KEY (UserID) REFERENCES public.Users(UserID),
  CONSTRAINT fk_answer_question FOREIGN KEY (QuestionID) REFERENCES public.SecurityQuestions(QuestionID)
);

CREATE TABLE public.Users (
  UserID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  Username text NOT NULL UNIQUE,
  PasswordHash text NOT NULL,
  FirstName text NOT NULL,
  LastName text NOT NULL,
  Email text NOT NULL UNIQUE,
  DOB date,
  Address text,
  ProfilePictureURL text,
  RoleID integer NOT NULL DEFAULT 3,
  IsActive boolean NOT NULL DEFAULT true,
  IsSuspended boolean NOT NULL DEFAULT false,
  FailedLoginAttempts integer NOT NULL DEFAULT 0,
  PasswordExpiryDate timestamp with time zone,
  SuspensionEndDate timestamp with time zone,
  DateCreated timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT Users_pkey PRIMARY KEY (UserID),
  CONSTRAINT fk_user_role FOREIGN KEY (RoleID) REFERENCES public.Roles(RoleID)
);
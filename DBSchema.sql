-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.chart_of_accounts (
  accountid integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  accountnumber text NOT NULL UNIQUE,
  accountname text NOT NULL UNIQUE,
  accountdescription text,
  normalside text NOT NULL CHECK (normalside = ANY (ARRAY['Debit'::text, 'Credit'::text])),
  category text NOT NULL,
  subcategory text,
  initialbalance numeric NOT NULL DEFAULT 0.00,
  displayorder integer,
  statementtype text CHECK (statementtype = ANY (ARRAY['BS'::text, 'IS'::text, 'RE'::text])),
  isactive boolean NOT NULL DEFAULT true,
  datecreated timestamp with time zone NOT NULL DEFAULT now(),
  createdbyuserid integer NOT NULL,
  comment text,
  CONSTRAINT chart_of_accounts_pkey PRIMARY KEY (accountid),
  CONSTRAINT fk_chartofaccounts_user FOREIGN KEY (createdbyuserid) REFERENCES public.users(UserID)
);
CREATE TABLE public.cron_job_logs (
  id integer NOT NULL DEFAULT nextval('cron_job_logs_id_seq'::regclass),
  job_name character varying NOT NULL,
  execution_time timestamp with time zone DEFAULT now(),
  status character varying NOT NULL,
  response_body text,
  notes text,
  CONSTRAINT cron_job_logs_pkey PRIMARY KEY (id)
);
CREATE TABLE public.event_logs (
  logid integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  userid integer NOT NULL,
  timestamp timestamp with time zone NOT NULL DEFAULT now(),
  actiontype text NOT NULL,
  tablename text NOT NULL,
  recordid integer NOT NULL,
  beforevalue jsonb,
  aftervalue jsonb,
  CONSTRAINT event_logs_pkey PRIMARY KEY (logid),
  CONSTRAINT fk_eventlogs_user FOREIGN KEY (userid) REFERENCES public.users(UserID)
);
CREATE TABLE public.password_history (
  PasswordHistoryID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  UserID integer NOT NULL,
  PasswordHash character varying NOT NULL,
  DateSet timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT password_history_pkey PRIMARY KEY (PasswordHistoryID),
  CONSTRAINT fk_password_history_user FOREIGN KEY (UserID) REFERENCES public.users(UserID)
);
CREATE TABLE public.registration_requests (
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
  RejectionReason text,
  CONSTRAINT registration_requests_pkey PRIMARY KEY (RequestID),
  CONSTRAINT fk_reviewed_by_user FOREIGN KEY (ReviewedByUserID) REFERENCES public.users(UserID)
);
CREATE TABLE public.roles (
  RoleID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  RoleName character varying NOT NULL UNIQUE,
  CONSTRAINT roles_pkey PRIMARY KEY (RoleID)
);
CREATE TABLE public.security_questions (
  QuestionID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  QuestionText character varying NOT NULL UNIQUE,
  CONSTRAINT security_questions_pkey PRIMARY KEY (QuestionID)
);
CREATE TABLE public.signup_invitations (
  InvitationID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  RequestID integer NOT NULL,
  Token text NOT NULL UNIQUE,
  ExpiresAt timestamp with time zone NOT NULL,
  UsedAt timestamp with time zone,
  CONSTRAINT signup_invitations_pkey PRIMARY KEY (InvitationID),
  CONSTRAINT signup_invitations_RequestID_fkey FOREIGN KEY (RequestID) REFERENCES public.registration_requests(RequestID)
);
CREATE TABLE public.user_security_answers (
  UserAnswerID integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  UserID integer NOT NULL,
  QuestionID integer NOT NULL,
  AnswerHash character varying NOT NULL,
  CONSTRAINT user_security_answers_pkey PRIMARY KEY (UserAnswerID),
  CONSTRAINT fk_answer_user FOREIGN KEY (UserID) REFERENCES public.users(UserID),
  CONSTRAINT fk_answer_question FOREIGN KEY (QuestionID) REFERENCES public.security_questions(QuestionID)
);
CREATE TABLE public.users (
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
  SuspensionReason text,
  AuthUID uuid UNIQUE,
  CONSTRAINT users_pkey PRIMARY KEY (UserID),
  CONSTRAINT fk_user_role FOREIGN KEY (RoleID) REFERENCES public.roles(RoleID),
  CONSTRAINT fk_users_auth FOREIGN KEY (AuthUID) REFERENCES auth.users(id)
);
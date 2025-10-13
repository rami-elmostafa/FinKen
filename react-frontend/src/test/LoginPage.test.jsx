import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';

describe('LoginPage', () => {
  it('renders login form with all required elements', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    // Check for branding
    expect(screen.getByText('PocketWatch', { exact: false })).toBeInTheDocument();
    expect(screen.getByText('Financial Accounting Application')).toBeInTheDocument();

    // Check for form elements
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();

    // Check for links
    expect(screen.getByText('Forgot Password?')).toBeInTheDocument();
    expect(screen.getByText('Create New User Account')).toBeInTheDocument();
  });

  it('displays required field indicators', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    const requiredIndicators = screen.getAllByText('*');
    expect(requiredIndicators.length).toBeGreaterThanOrEqual(2); // Username and Password
  });
});

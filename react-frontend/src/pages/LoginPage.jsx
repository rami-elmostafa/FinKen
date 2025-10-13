import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import FlashMessages from '../components/ui/FlashMessage';

// Validation schema
const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

/**
 * LoginPage - Sign in page for the application
 * Converted from: templates/index.html
 */
function LoginPage() {
  const navigate = useNavigate();
  const [flashMessages, setFlashMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    setFlashMessages([]);

    try {
      // TODO: Replace with actual API call to Flask backend
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        credentials: 'include', // Important for session cookies
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setFlashMessages([
          {
            id: Date.now(),
            type: 'success',
            message: result.message || 'Login successful!',
            duration: 2000,
          },
        ]);
        
        // Redirect to home page after short delay
        setTimeout(() => {
          navigate('/home');
        }, 1000);
      } else {
        setFlashMessages([
          {
            id: Date.now(),
            type: 'error',
            message: result.message || 'Login failed. Please check your credentials.',
          },
        ]);
      }
    } catch (error) {
      console.error('Login error:', error);
      setFlashMessages([
        {
          id: Date.now(),
          type: 'error',
          message: 'An error occurred. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const dismissMessage = (id) => {
    setFlashMessages((prev) => prev.filter((msg) => msg.id !== id));
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-400">
      {/* Header with Branding */}
      <div className="flex justify-between items-center min-h-[200px] px-10">
        <div className="flex-1 flex justify-center">
          <div className="flex items-center gap-3">
            <img
              src="/finkenlogo.png"
              alt="FinKen Logo"
              className="h-40 w-auto object-contain"
            />
            <div className="text-left">
              <h1 className="text-4xl font-semibold mb-1">
                <span className="text-black">Pocket</span>
                <span className="text-primary-dark">Watch</span>
              </h1>
              <p className="text-black text-base font-normal">
                Financial Accounting Application
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Flash Messages */}
      <FlashMessages messages={flashMessages} onDismiss={dismissMessage} />

      {/* Main Content */}
      <div className="w-full max-w-[500px] mx-auto px-5 flex items-center justify-center min-h-[20vh]">
        {/* Login Container */}
        <div 
          className="bg-white border-2 border-gray-300 rounded-card shadow-card w-full"
          style={{ animation: 'fadeIn 0.5s ease-out' }}
        >
          <div className="px-16 py-12">
            <h2 className="text-gray-900 text-3xl mb-8 text-center font-medium">
              Sign In
            </h2>

            <form onSubmit={handleSubmit(onSubmit)}>
              <Input
                label="Username"
                type="text"
                placeholder="Enter your username"
                error={errors.username?.message}
                {...register('username')}
                required
              />

              <Input
                label="Password"
                type="password"
                placeholder="Enter your password"
                error={errors.password?.message}
                {...register('password')}
                required
              />

              <Button
                type="submit"
                variant="primary"
                className="w-full mb-2"
                disabled={isLoading}
              >
                {isLoading ? 'Signing In...' : 'Sign In'}
              </Button>
            </form>

            {/* Action Links */}
            <div className="mt-8 text-center">
              <Link
                to="/forgot-password"
                className="block py-3 text-gray-700 font-normal hover:text-gray-900 hover:underline transition-colors"
              >
                Forgot Password?
              </Link>
              <Link to="/create-new-user">
                <Button variant="secondary" className="w-full">
                  Create New User Account
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;

import PropTypes from 'prop-types';
import { forwardRef } from 'react';

/**
 * Input Component - Reusable text input with error handling
 */
const Input = forwardRef(function Input(
  { 
    label, 
    error, 
    helpText,
    required = false,
    className = '',
    containerClassName = '',
    ...props 
  }, 
  ref
) {
  const inputId = props.id || props.name;

  return (
    <div className={`mb-4 ${containerClassName}`}>
      {label && (
        <label 
          htmlFor={inputId}
          className="block mb-2 font-normal text-gray-700 text-sm"
        >
          {label}
          {required && <span className="text-red-600 ml-1">*</span>}
        </label>
      )}
      
      <input
        ref={ref}
        id={inputId}
        className={`
          w-full px-3.5 py-3.5 border rounded
          text-base transition-all duration-300 bg-white
          ${error 
            ? 'border-red-500 focus:border-red-500 focus:ring-2 focus:ring-red-200' 
            : 'border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary/20'
          }
          focus:outline-none
          disabled:bg-gray-100 disabled:cursor-not-allowed
          ${className}
        `}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${inputId}-error` : helpText ? `${inputId}-help` : undefined}
        {...props}
      />
      
      {helpText && !error && (
        <p id={`${inputId}-help`} className="mt-1 text-xs text-gray-600">
          {helpText}
        </p>
      )}
      
      {error && (
        <p id={`${inputId}-error`} className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
});

Input.propTypes = {
  label: PropTypes.string,
  error: PropTypes.string,
  helpText: PropTypes.string,
  required: PropTypes.bool,
  className: PropTypes.string,
  containerClassName: PropTypes.string,
  id: PropTypes.string,
  name: PropTypes.string,
};

export default Input;

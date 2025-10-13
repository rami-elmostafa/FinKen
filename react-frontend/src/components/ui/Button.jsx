import PropTypes from 'prop-types';

/**
 * Button Component - Reusable button with variants
 */
function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  type = 'button',
  disabled = false,
  onClick,
  className = '',
  ...props 
}) {
  const baseStyles = 'inline-block font-medium text-center rounded-lg transition-all duration-200 cursor-pointer border disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantStyles = {
    primary: 'bg-primary hover:bg-primary-dark text-secondary border-primary-dark font-semibold hover:shadow-elevated',
    secondary: 'bg-transparent text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400',
    success: 'bg-accent-green hover:bg-green-600 text-white border-accent-green',
    danger: 'bg-accent-red hover:bg-red-600 text-white border-accent-red',
    warning: 'bg-accent-yellow hover:bg-yellow-600 text-gray-900 border-accent-yellow',
    link: 'bg-transparent text-gray-700 border-none hover:text-gray-900 hover:underline shadow-none',
  };
  
  const sizeStyles = {
    small: 'px-3 py-1.5 text-sm',
    medium: 'px-6 py-3 text-base',
    large: 'px-8 py-4 text-lg',
  };

  const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`;

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={combinedClassName}
      {...props}
    >
      {children}
    </button>
  );
}

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'success', 'danger', 'warning', 'link']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  disabled: PropTypes.bool,
  onClick: PropTypes.func,
  className: PropTypes.string,
};

export default Button;

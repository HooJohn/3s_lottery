import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, Check, ChevronDown } from 'lucide-react';
import { availableLanguages, changeLanguage, getCurrentLanguage } from '@/i18n';
import { cn } from '@/utils/cn';

interface LanguageSwitcherProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'button' | 'dropdown';
  className?: string;
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  size = 'md',
  variant = 'dropdown',
  className,
}) => {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [isChanging, setIsChanging] = useState(false);
  
  const currentLanguage = getCurrentLanguage();

  const handleLanguageChange = async (languageCode: string) => {
    if (languageCode === i18n.language || isChanging) return;
    
    setIsChanging(true);
    try {
      await changeLanguage(languageCode);
      setIsOpen(false);
    } catch (error) {
      console.error('Failed to change language:', error);
    } finally {
      setIsChanging(false);
    }
  };

  const sizeClasses = {
    sm: 'text-sm px-2 py-1',
    md: 'text-base px-3 py-2',
    lg: 'text-lg px-4 py-3',
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  if (variant === 'button') {
    return (
      <div className={cn('flex space-x-1', className)}>
        {availableLanguages.map((language) => (
          <button
            key={language.code}
            onClick={() => handleLanguageChange(language.code)}
            disabled={isChanging}
            className={cn(
              'flex items-center space-x-1 rounded-lg transition-all duration-200',
              sizeClasses[size],
              language.code === i18n.language
                ? 'bg-primary-100 text-primary-700 font-medium'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
              isChanging && 'opacity-50 cursor-not-allowed'
            )}
          >
            <span className="text-lg">{language.flag}</span>
            <span className="hidden sm:inline">{language.code.toUpperCase()}</span>
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className={cn('relative', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isChanging}
        className={cn(
          'flex items-center space-x-2 rounded-lg border border-gray-200 bg-white transition-all duration-200',
          'hover:border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
          sizeClasses[size],
          isChanging && 'opacity-50 cursor-not-allowed'
        )}
      >
        <Globe className={cn(iconSizes[size], 'text-gray-500')} />
        <span className="flex items-center space-x-1">
          <span className="text-lg">{currentLanguage.flag}</span>
          <span className="hidden sm:inline font-medium">{currentLanguage.name}</span>
          <span className="sm:hidden font-medium">{currentLanguage.code.toUpperCase()}</span>
        </span>
        <ChevronDown 
          className={cn(
            iconSizes[size], 
            'text-gray-400 transition-transform duration-200',
            isOpen && 'rotate-180'
          )} 
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* 遮罩层 */}
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
            />
            
            {/* 下拉菜单 */}
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="absolute top-full left-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-heavy z-20"
            >
              <div className="py-2">
                {availableLanguages.map((language) => (
                  <button
                    key={language.code}
                    onClick={() => handleLanguageChange(language.code)}
                    disabled={isChanging}
                    className={cn(
                      'w-full flex items-center justify-between px-4 py-3 text-left transition-colors duration-200',
                      'hover:bg-gray-50 focus:outline-none focus:bg-gray-50',
                      language.code === i18n.language
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700',
                      isChanging && 'opacity-50 cursor-not-allowed'
                    )}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-xl">{language.flag}</span>
                      <div>
                        <div className="font-medium">{language.name}</div>
                        <div className="text-sm text-gray-500">{language.code.toUpperCase()}</div>
                      </div>
                    </div>
                    
                    {language.code === i18n.language && (
                      <Check className="w-4 h-4 text-primary-600" />
                    )}
                  </button>
                ))}
              </div>
              
              {/* 底部提示 */}
              <div className="border-t border-gray-100 px-4 py-2">
                <p className="text-xs text-gray-500">
                  {process.env.NODE_ENV === 'development' 
                    ? '开发环境显示所有语言' 
                    : '生产环境仅显示英语和法语'
                  }
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default LanguageSwitcher;
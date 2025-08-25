import React, { useState, useRef, useEffect, memo } from 'react'
import { cn } from '@/utils/cn'

interface LazyImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string
  alt: string
  placeholder?: string
  fallback?: string
  className?: string
  containerClassName?: string
  threshold?: number
  rootMargin?: string
  onLoad?: () => void
  onError?: () => void
  blur?: boolean
  progressive?: boolean
}

const LazyImage = memo<LazyImageProps>(({
  src,
  alt,
  placeholder,
  fallback,
  className,
  containerClassName,
  threshold = 0.1,
  rootMargin = '50px',
  onLoad,
  onError,
  blur = true,
  progressive = false,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false)
  const [isError, setIsError] = useState(false)
  const [isInView, setIsInView] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Intersection Observer for lazy loading
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true)
          observer.disconnect()
        }
      },
      {
        threshold,
        rootMargin
      }
    )

    observer.observe(container)

    return () => {
      observer.disconnect()
    }
  }, [threshold, rootMargin])

  // Handle image loading
  useEffect(() => {
    if (!isInView || isLoaded || isError) return

    const img = new Image()
    
    img.onload = () => {
      setIsLoaded(true)
      onLoad?.()
    }

    img.onerror = () => {
      setIsError(true)
      onError?.()
    }

    // Progressive loading: load low quality first, then high quality
    if (progressive && placeholder) {
      const lowQualityImg = new Image()
      lowQualityImg.onload = () => {
        if (imgRef.current) {
          imgRef.current.src = placeholder
        }
      }
      lowQualityImg.src = placeholder
    }

    img.src = src
  }, [isInView, src, placeholder, progressive, isLoaded, isError, onLoad, onError])

  const handleImageLoad = () => {
    setIsLoaded(true)
    onLoad?.()
  }

  const handleImageError = () => {
    setIsError(true)
    onError?.()
  }

  const getImageSrc = () => {
    if (isError && fallback) return fallback
    if (!isInView) return placeholder || ''
    if (progressive && placeholder && !isLoaded) return placeholder
    return src
  }

  return (
    <div
      ref={containerRef}
      className={cn('relative overflow-hidden', containerClassName)}
    >
      {/* Placeholder/Loading state */}
      {!isLoaded && !isError && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center">
          {placeholder ? (
            <img
              src={placeholder}
              alt={alt}
              className={cn(
                'w-full h-full object-cover',
                blur && 'filter blur-sm',
                className
              )}
            />
          ) : (
            <div className="w-8 h-8 text-gray-400">
              <svg
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fillRule="evenodd"
                  d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
        </div>
      )}

      {/* Error state */}
      {isError && !fallback && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <div className="text-center text-gray-500">
            <div className="w-8 h-8 mx-auto mb-2">
              <svg
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <span className="text-sm">加载失败</span>
          </div>
        </div>
      )}

      {/* Actual image */}
      {isInView && (
        <img
          ref={imgRef}
          src={getImageSrc()}
          alt={alt}
          className={cn(
            'w-full h-full object-cover transition-opacity duration-300',
            isLoaded ? 'opacity-100' : 'opacity-0',
            className
          )}
          onLoad={handleImageLoad}
          onError={handleImageError}
          {...props}
        />
      )}
    </div>
  )
})

LazyImage.displayName = 'LazyImage'

export default LazyImage

// 预加载图片的工具函数
export const preloadImage = (src: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve()
    img.onerror = reject
    img.src = src
  })
}

// 批量预加载图片
export const preloadImages = (srcs: string[]): Promise<void[]> => {
  return Promise.all(srcs.map(preloadImage))
}

// 生成不同尺寸的图片URL（用于响应式图片）
export const generateResponsiveImageUrls = (
  baseUrl: string,
  sizes: number[] = [320, 640, 768, 1024, 1280, 1920]
): Array<{ src: string; width: number }> => {
  return sizes.map(size => ({
    src: `${baseUrl}?w=${size}&q=75`,
    width: size
  }))
}

// 响应式图片组件
interface ResponsiveImageProps extends Omit<LazyImageProps, 'src'> {
  src: string
  sizes?: string
  breakpoints?: number[]
}

export const ResponsiveImage = memo<ResponsiveImageProps>(({
  src,
  sizes = '100vw',
  breakpoints = [320, 640, 768, 1024, 1280, 1920],
  ...props
}) => {
  const imageUrls = generateResponsiveImageUrls(src, breakpoints)
  
  const srcSet = imageUrls
    .map(({ src, width }) => `${src} ${width}w`)
    .join(', ')

  return (
    <LazyImage
      src={src}
      srcSet={srcSet}
      sizes={sizes}
      {...props}
    />
  )
})

ResponsiveImage.displayName = 'ResponsiveImage'
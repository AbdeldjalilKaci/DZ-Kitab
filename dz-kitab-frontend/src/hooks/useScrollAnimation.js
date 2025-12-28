import { useEffect, useRef } from 'react';

/**
 * Custom hook for scroll-triggered animations
 * @param {string} animationType - Type of animation: 'fade-up', 'fade-left', 'fade-right', 'scale', 'slide-left', 'slide-right'
 * @param {number} delay - Delay before animation starts (in ms)
 * @param {number} threshold - Percentage of element visible before triggering (0-1)
 */
export const useScrollAnimation = (animationType = 'fade-up', delay = 0, threshold = 0.1) => {
    const elementRef = useRef(null);

    useEffect(() => {
        const element = elementRef.current;
        if (!element) return;

        // Add initial hidden state
        element.style.opacity = '0';
        element.style.transform = getInitialTransform(animationType);
        element.style.transition = `opacity 0.8s ease-out ${delay}ms, transform 0.8s ease-out ${delay}ms`;

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        // Trigger animation
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translate(0, 0) scale(1)';
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold }
        );

        observer.observe(element);

        return () => {
            if (element) observer.unobserve(element);
        };
    }, [animationType, delay, threshold]);

    return elementRef;
};

const getInitialTransform = (type) => {
    switch (type) {
        case 'fade-up':
            return 'translateY(50px)';
        case 'fade-down':
            return 'translateY(-50px)';
        case 'fade-left':
            return 'translateX(50px)';
        case 'fade-right':
            return 'translateX(-50px)';
        case 'slide-left':
            return 'translateX(100px)';
        case 'slide-right':
            return 'translateX(-100px)';
        case 'scale':
            return 'scale(0.8)';
        case 'zoom':
            return 'scale(0.5)';
        default:
            return 'translateY(50px)';
    }
};

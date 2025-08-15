/**
 * Mobile-Specific Analytics for Art Explorer
 * Tracks mobile Safari login/registration issues and user behavior
 */

import { track } from '@vercel/analytics';

class MobileAnalytics {
    constructor() {
        this.isMobile = this.detectMobile();
        this.isSafari = this.detectSafari();
        this.isIOS = this.detectIOS();
        this.deviceInfo = this.getDeviceInfo();
        this.initializeTracking();
    }

    /**
     * Detect if user is on mobile device
     */
    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               (navigator.maxTouchPoints && navigator.maxTouchPoints > 2);
    }

    /**
     * Detect Safari browser
     */
    detectSafari() {
        return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    }

    /**
     * Detect iOS device
     */
    detectIOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent);
    }

    /**
     * Get detailed device information
     */
    getDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            doNotTrack: navigator.doNotTrack,
            screenWidth: screen.width,
            screenHeight: screen.height,
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
            deviceMemory: navigator.deviceMemory || 'unknown',
            hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
            maxTouchPoints: navigator.maxTouchPoints || 0,
            connection: this.getConnectionInfo(),
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            isMobile: this.isMobile,
            isSafari: this.isSafari,
            isIOS: this.isIOS
        };
    }

    /**
     * Get network connection information
     */
    getConnectionInfo() {
        if ('connection' in navigator) {
            return {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt,
                saveData: navigator.connection.saveData
            };
        }
        return 'Not supported';
    }

    /**
     * Initialize mobile-specific tracking
     */
    initializeTracking() {
        if (this.isMobile) {
            this.trackMobileSession();
            this.trackMobileCapabilities();
            this.trackMobilePerformance();
        }
    }

    /**
     * Track mobile session start
     */
    trackMobileSession() {
        track('mobile_session_start', {
            device: this.isIOS ? 'iOS' : 'Android',
            browser: this.isSafari ? 'Safari' : 'Other',
            screenSize: `${this.deviceInfo.screenWidth}x${this.deviceInfo.screenHeight}`,
            viewport: `${this.deviceInfo.viewportWidth}x${this.deviceInfo.viewportHeight}`,
            connection: this.deviceInfo.connection,
            userAgent: this.deviceInfo.userAgent
        });
    }

    /**
     * Track mobile device capabilities
     */
    trackMobileCapabilities() {
        track('mobile_capabilities', {
            touchSupport: this.deviceInfo.maxTouchPoints > 0,
            maxTouchPoints: this.deviceInfo.maxTouchPoints,
            deviceMemory: this.deviceInfo.deviceMemory,
            hardwareConcurrency: this.deviceInfo.hardwareConcurrency,
            cookieEnabled: this.deviceInfo.cookieEnabled,
            doNotTrack: this.deviceInfo.doNotTrack
        });
    }

    /**
     * Track mobile performance metrics
     */
    trackMobilePerformance() {
        if ('performance' in window) {
            window.addEventListener('load', () => {
                const perf = performance.getEntriesByType('navigation')[0];
                if (perf) {
                    track('mobile_performance', {
                        pageLoadTime: perf.loadEventEnd - perf.loadEventStart,
                        domContentLoaded: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
                        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
                        device: this.isIOS ? 'iOS' : 'Android',
                        browser: this.isSafari ? 'Safari' : 'Other'
                    });
                }
            });
        }
    }

    /**
     * Track login attempt
     */
    trackLoginAttempt(credentials, success = false, error = null) {
        const eventData = {
            success,
            device: this.isIOS ? 'iOS' : 'Android',
            browser: this.isSafari ? 'Safari' : 'Other',
            screenSize: `${this.deviceInfo.screenWidth}x${this.deviceInfo.screenHeight}`,
            viewport: `${this.deviceInfo.viewportWidth}x${this.deviceInfo.viewportHeight}`,
            connection: this.deviceInfo.connection,
            hasEmail: !!credentials.email,
            hasUsername: !!credentials.username,
            timestamp: new Date().toISOString()
        };

        if (error) {
            eventData.error = error.message || error.toString();
            eventData.errorType = error.name || 'Unknown';
            eventData.errorStack = error.stack;
        }

        track('login_attempt', eventData);
    }

    /**
     * Track registration attempt
     */
    trackRegistrationAttempt(credentials, success = false, error = null) {
        const eventData = {
            success,
            device: this.isIOS ? 'iOS' : 'Android',
            browser: this.isSafari ? 'Safari' : 'Other',
            screenSize: `${this.deviceInfo.screenWidth}x${this.deviceInfo.screenHeight}`,
            viewport: `${this.deviceInfo.viewportWidth}x${this.deviceInfo.viewportHeight}`,
            connection: this.deviceInfo.connection,
            hasEmail: !!credentials.email,
            hasUsername: !!credentials.username,
            passwordLength: credentials.password?.length || 0,
            timestamp: new Date().toISOString()
        };

        if (error) {
            eventData.error = error.message || error.toString();
            eventData.errorType = error.name || 'Unknown';
            eventData.errorStack = error.stack;
        }

        track('registration_attempt', eventData);
    }

    /**
     * Track form interaction issues
     */
    trackFormIssue(formType, issue, details = {}) {
        track('mobile_form_issue', {
            formType, // 'login' or 'register'
            issue, // 'validation_error', 'network_error', 'submit_failure', etc.
            device: this.isIOS ? 'iOS' : 'Android',
            browser: this.isSafari ? 'Safari' : 'Other',
            screenSize: `${this.deviceInfo.screenWidth}x${this.deviceInfo.screenHeight}`,
            viewport: `${this.deviceInfo.viewportWidth}x${this.deviceInfo.viewportHeight}`,
            connection: this.deviceInfo.connection,
            details,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Track mobile-specific errors
     */
    trackMobileError(error, context = {}) {
        track('mobile_error', {
            error: error.message || error.toString(),
            errorType: error.name || 'Unknown',
            errorStack: error.stack,
            device: this.isIOS ? 'iOS' : 'Android',
            browser: this.isSafari ? 'Safari' : 'Other',
            screenSize: `${this.deviceInfo.screenWidth}x${this.deviceInfo.screenHeight}`,
            viewport: `${this.deviceInfo.viewportWidth}x${this.deviceInfo.viewportHeight}`,
            connection: this.deviceInfo.connection,
            context,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Track mobile user behavior
     */
    trackMobileBehavior(action, details = {}) {
        track('mobile_behavior', {
            action,
            device: this.isIOS ? 'iOS' : 'Android',
            browser: this.isSafari ? 'Safari' : 'Other',
            screenSize: `${this.deviceInfo.screenWidth}x${this.deviceInfo.screenHeight}`,
            viewport: `${this.deviceInfo.viewportWidth}x${this.deviceInfo.viewportHeight}`,
            connection: this.deviceInfo.connection,
            details,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Track mobile viewport changes
     */
    trackViewportChange() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                const newViewport = {
                    width: window.innerWidth,
                    height: window.innerHeight
                };
                
                if (newViewport.width !== this.deviceInfo.viewportWidth || 
                    newViewport.height !== this.deviceInfo.viewportHeight) {
                    
                    this.deviceInfo.viewportWidth = newViewport.width;
                    this.deviceInfo.viewportHeight = newViewport.height;
                    
                    track('mobile_viewport_change', {
                        oldViewport: `${this.deviceInfo.screenWidth}x${this.deviceInfo.screenHeight}`,
                        newViewport: `${newViewport.width}x${newViewport.height}`,
                        device: this.isIOS ? 'iOS' : 'Android',
                        browser: this.isSafari ? 'Safari' : 'Other',
                        orientation: newViewport.width > newViewport.height ? 'landscape' : 'portrait'
                    });
                }
            }, 250);
        });
    }

    /**
     * Track mobile orientation changes
     */
    trackOrientationChange() {
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                track('mobile_orientation_change', {
                    orientation: window.orientation === 0 ? 'portrait' : 'landscape',
                    device: this.isIOS ? 'iOS' : 'Android',
                    browser: this.isSafari ? 'Safari' : 'Other',
                    screenSize: `${this.deviceInfo.screenWidth}x${this.deviceInfo.screenHeight}`,
                    viewport: `${this.deviceInfo.viewportWidth}x${this.deviceInfo.viewportHeight}`,
                    timestamp: new Date().toISOString()
                });
            }, 100);
        });
    }

    /**
     * Get current device status
     */
    getDeviceStatus() {
        return {
            isMobile: this.isMobile,
            isSafari: this.isSafari,
            isIOS: this.isIOS,
            deviceInfo: this.deviceInfo
        };
    }

    /**
     * Check if current device is problematic for auth
     */
    isProblematicDevice() {
        return this.isMobile && this.isSafari && this.isIOS;
    }
}

// Export singleton instance
export const mobileAnalytics = new MobileAnalytics();

// Export for direct use
export default mobileAnalytics;

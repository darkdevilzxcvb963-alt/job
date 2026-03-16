
import { useEffect } from 'react';

const useOneSignal = (user) => {
  useEffect(() => {
    // Check if OneSignal is already loaded via the script tag
    const OneSignal = window.OneSignal || [];

    const initOneSignal = async () => {
      try {
        if (!window.OneSignal) {
          console.warn('OneSignal SDK not loaded yet.');
          return;
        }

        await window.OneSignal.init({
          appId: "6b3a9a67-2853-4f09-a0c2-f29dc4ef23ca",
          allowLocalhostAsSecureOrigin: true,
          notifyButton: {
            enable: true,
          },
        });

        // Link the logged-in user to OneSignal using their ID/Email
        if (user) {
          // Use user ID (or email if ID is not available) as external ID
          const externalId = user.id || user.email;
          if (externalId) {
            console.log('Setting OneSignal External User ID:', externalId);
            await window.OneSignal.setExternalUserId(externalId);
          }
        } else {
          // If no user is logged in, remove the external ID
          console.log('Removing OneSignal External User Id');
          await window.OneSignal.removeExternalUserId();
        }
      } catch (error) {
        console.error('OneSignal initialization error:', error);
      }
    };

    initOneSignal();
  }, [user]);
};

export default useOneSignal;

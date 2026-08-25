import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from 'react';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
  sendPasswordResetEmail,
  User as FirebaseUser,
} from 'firebase/auth';
import { firebaseAuth } from '../lib/firebase';
import { syncUserProfile, logUserActivity } from '../lib/firestoreService';

// Keep the same User shape the rest of the app uses
export interface User {
  id: string;
  email: string;
  display_name: string;
}

interface AuthContextType {
  user: User | null;
  firebaseUser: FirebaseUser | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Listen to Firebase auth state changes
    const unsubscribe = onAuthStateChanged(firebaseAuth, async (fbUser) => {
      if (fbUser) {
        setFirebaseUser(fbUser);
        const userData: User = {
          id: fbUser.uid,
          email: fbUser.email ?? '',
          display_name: fbUser.displayName ?? 'Doctor',
        };
        setUser(userData);

        // Immediately sync user profile to Firestore users/{uid}
        await syncUserProfile(fbUser, { displayName: fbUser.displayName || 'Doctor' });
      } else {
        setFirebaseUser(null);
        setUser(null);
      }
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const login = async (email: string, password: string) => {
    const result = await signInWithEmailAndPassword(firebaseAuth, email, password);
    const fbUser = result.user;
    
    // Sync profile and log login action
    await syncUserProfile(fbUser, { displayName: fbUser.displayName || 'Doctor' });
    await logUserActivity(fbUser.uid, fbUser.email || email, fbUser.displayName || 'Doctor', 'login');
  };

  const register = async (email: string, password: string, name: string) => {
    const result = await createUserWithEmailAndPassword(firebaseAuth, email, password);
    await updateProfile(result.user, { displayName: name });
    
    setUser({
      id: result.user.uid,
      email: result.user.email ?? '',
      display_name: name,
    });

    // Save complete new user profile to Firestore users/{uid} and log registration
    await syncUserProfile(result.user, { displayName: name, isNewUser: true });
    await logUserActivity(result.user.uid, result.user.email || email, name, 'register');
  };

  const resetPassword = async (email: string) => {
    await sendPasswordResetEmail(firebaseAuth, email);
    await logUserActivity('', email, '', 'password_reset');
  };

  const logout = () => {
    if (firebaseUser) {
      logUserActivity(firebaseUser.uid, firebaseUser.email || '', firebaseUser.displayName || '', 'logout');
    }
    signOut(firebaseAuth);
  };

  return (
    <AuthContext.Provider value={{ user, firebaseUser, login, register, resetPassword, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}


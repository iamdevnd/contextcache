
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import AdminLayout from '@/components/admin/AdminLayout';
import { FiLock, FiKey, FiShield, FiAlertCircle } from 'react-icons/fi';
import toast from 'react-hot-toast';

export default function AdminSecurityPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  if (!isAuthenticated || user?.username !== 'admin') {
    router.push('/');
    return null;
  }

  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 8) {
      toast.error('Password must be at least 8 characters long');
      return;
    }

    // TODO: Implement password change API endpoint
    toast.success('Password change feature coming soon');
    setShowPasswordForm(false);
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
  };

  return (
    <AdminLayout>
      <div className="max-w-4xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Security Settings</h1>
          <p className="text-gray-400">Manage authentication and access control</p>
        </div>

        {/* Security Overview */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <FiShield className="mr-2" />
            Security Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-700 p-4 rounded-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Authentication</span>
                <span className="text-xs bg-green-600 px-2 py-1 rounded">Active</span>
              </div>
              <p className="font-semibold">JWT Token</p>
            </div>
            <div className="bg-gray-700 p-4 rounded-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Encryption</span>
                <span className="text-xs bg-green-600 px-2 py-1 rounded">Active</span>
              </div>
              <p className="font-semibold">bcrypt + HS256</p>
            </div>
            <div className="bg-gray-700 p-4 rounded-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Rate Limiting</span>
                <span className="text-xs bg-green-600 px-2 py-1 rounded">Active</span>
              </div>
              <p className="font-semibold">Enabled</p>
           </div>
         </div>
       </div>

       {/* Password Management */}
       <div className="bg-gray-800 rounded-lg p-6 mb-6">
         <h2 className="text-xl font-semibold mb-4 flex items-center">
           <FiKey className="mr-2" />
           Admin Password
         </h2>
         {!showPasswordForm ? (
           <div>
             <p className="text-gray-400 mb-4">
               Change the admin account password. Make sure to use a strong password.
             </p>
             <button
               onClick={() => setShowPasswordForm(true)}
               className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition"
             >
               Change Password
             </button>
           </div>
         ) : (
           <div className="space-y-4">
             <div>
               <label className="block text-sm font-medium mb-2">Current Password</label>
               <input
                 type="password"
                 value={passwordData.currentPassword}
                 onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                 className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
               />
             </div>
             <div>
               <label className="block text-sm font-medium mb-2">New Password</label>
               <input
                 type="password"
                 value={passwordData.newPassword}
                 onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                 className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
               />
             </div>
             <div>
               <label className="block text-sm font-medium mb-2">Confirm New Password</label>
               <input
                 type="password"
                 value={passwordData.confirmPassword}
                 onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                 className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
               />
             </div>
             <div className="flex space-x-4">
               <button
                 onClick={() => {
                   setShowPasswordForm(false);
                   setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
                 }}
                 className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md transition"
               >
                 Cancel
               </button>
               <button
                 onClick={handlePasswordChange}
                 className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition"
               >
                 Update Password
               </button>
             </div>
           </div>
         )}
       </div>

       {/* Security Recommendations */}
       <div className="bg-gray-800 rounded-lg p-6">
         <h2 className="text-xl font-semibold mb-4 flex items-center">
           <FiAlertCircle className="mr-2" />
           Security Recommendations
         </h2>
         <ul className="space-y-3 text-gray-300">
           <li className="flex items-start">
             <span className="text-green-500 mr-2">✓</span>
             <span>Use strong passwords with at least 8 characters, including uppercase, lowercase, numbers, and symbols</span>
           </li>
           <li className="flex items-start">
             <span className="text-green-500 mr-2">✓</span>
             <span>Regularly update the JWT secret key in production environments</span>
           </li>
           <li className="flex items-start">
             <span className="text-green-500 mr-2">✓</span>
             <span>Monitor rate limit violations in the logs for potential abuse</span>
           </li>
           <li className="flex items-start">
             <span className="text-green-500 mr-2">✓</span>
             <span>Keep the application and dependencies up to date</span>
           </li>
           <li className="flex items-start">
             <span className="text-green-500 mr-2">✓</span>
             <span>Use HTTPS in production to encrypt data in transit</span>
           </li>
         </ul>
       </div>
     </div>
   </AdminLayout>
 );
}
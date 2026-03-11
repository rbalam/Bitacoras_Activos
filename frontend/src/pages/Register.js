import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card } from '../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from 'sonner';
import { User, Mail, Lock, Phone, Loader2 } from 'lucide-react';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'tecnico',
    phone: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await register(formData);
    
    if (result.success) {
      toast.success('¡Cuenta creada exitosamente!');
      navigate('/dashboard');
    } else {
      toast.error(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-slate-50" data-testid="register-page">
      <Card className="w-full max-w-md p-8 bg-white border border-slate-200 shadow-sm rounded-sm">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Chivo, sans-serif' }}>
            Crear Cuenta
          </h2>
          <p className="text-slate-600">Completa el formulario para registrarte</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <Label htmlFor="full_name" className="text-sm font-bold uppercase tracking-wider text-slate-600">
              Nombre Completo
            </Label>
            <div className="mt-2 relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <Input
                id="full_name"
                type="text"
                required
                data-testid="fullname-input"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="pl-10 bg-white border-slate-200 focus:ring-2 focus:ring-slate-900/10 rounded-sm"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="email" className="text-sm font-bold uppercase tracking-wider text-slate-600">
              Email
            </Label>
            <div className="mt-2 relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <Input
                id="email"
                type="email"
                required
                data-testid="email-input"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="pl-10 bg-white border-slate-200 focus:ring-2 focus:ring-slate-900/10 rounded-sm"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="phone" className="text-sm font-bold uppercase tracking-wider text-slate-600">
              Teléfono (Opcional)
            </Label>
            <div className="mt-2 relative">
              <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <Input
                id="phone"
                type="tel"
                data-testid="phone-input"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="pl-10 bg-white border-slate-200 focus:ring-2 focus:ring-slate-900/10 rounded-sm"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="role" className="text-sm font-bold uppercase tracking-wider text-slate-600">
              Rol
            </Label>
            <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
              <SelectTrigger className="mt-2 bg-white border-slate-200 rounded-sm" data-testid="role-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="admin">Administrador</SelectItem>
                <SelectItem value="gerente">Gerente</SelectItem>
                <SelectItem value="tecnico">Técnico</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="password" className="text-sm font-bold uppercase tracking-wider text-slate-600">
              Contraseña
            </Label>
            <div className="mt-2 relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <Input
                id="password"
                type="password"
                required
                data-testid="password-input"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="pl-10 bg-white border-slate-200 focus:ring-2 focus:ring-slate-900/10 rounded-sm"
              />
            </div>
          </div>

          <Button
            type="submit"
            disabled={loading}
            data-testid="register-button"
            className="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-sm font-medium shadow-sm"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creando cuenta...
              </>
            ) : (
              'Crear Cuenta'
            )}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-slate-600">
            ¿Ya tienes cuenta?{' '}
            <Link to="/login" className="font-semibold text-slate-900 hover:underline" data-testid="login-link">
              Iniciar Sesión
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Register;

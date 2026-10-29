import { cn } from './utils';

describe('cn utility function', () => {
  it('should merge basic class names', () => {
    expect(cn('class1', 'class2')).toBe('class1 class2');
  });

  it('should handle undefined and null inputs', () => {
    expect(cn('class1', undefined, 'class2', null)).toBe('class1 class2');
  });

  it('should handle conditional classes using objects', () => {
    expect(cn({ class1: true, class2: false, class3: true })).toBe('class1 class3');
  });

  it('should merge conflicting tailwind classes correctly', () => {
    expect(cn('p-4 p-8')).toBe('p-8');
    expect(cn('bg-red-500 bg-blue-500')).toBe('bg-blue-500');
    expect(cn('text-sm text-lg')).toBe('text-lg');
  });

  it('should handle complex combinations of inputs', () => {
    const isHovered = true;
    const isDisabled = false;

    expect(
      cn(
        'base-class',
        isHovered && 'hover-class',
        isDisabled && 'disabled-class',
        { 'conditional-class': true },
        ['array-class-1', 'array-class-2']
      )
    ).toBe('base-class hover-class conditional-class array-class-1 array-class-2');
  });

  it('should handle tailwind class conflicts within arrays and conditional objects', () => {
    expect(
      cn(
        'px-2 py-1',
        { 'px-4': true }, // px-4 overrides px-2
        ['bg-red-500', 'text-white'],
        'bg-blue-500' // bg-blue-500 overrides bg-red-500
      )
    ).toBe('py-1 px-4 text-white bg-blue-500');
  });
});

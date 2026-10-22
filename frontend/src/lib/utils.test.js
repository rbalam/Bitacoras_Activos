import { cn } from './utils';

describe('cn utility function', () => {
  it('should merge basic strings', () => {
    expect(cn('class-one', 'class-two')).toBe('class-one class-two');
  });

  it('should handle conditional classes', () => {
    expect(cn('class-one', { 'class-two': true, 'class-three': false })).toBe('class-one class-two');
  });

  it('should handle array inputs', () => {
    expect(cn(['class-one', 'class-two'])).toBe('class-one class-two');
  });

  it('should ignore falsy values', () => {
    expect(cn('class-one', null, undefined, false, '', 'class-two')).toBe('class-one class-two');
  });

  it('should correctly override tailwind utility classes', () => {
    // p-3 overrides px-2 and py-1
    expect(cn('px-2 py-1', 'p-3')).toBe('p-3');

    // bg-red-500 overrides bg-blue-500
    expect(cn('bg-blue-500 text-white', 'bg-red-500')).toBe('text-white bg-red-500');
  });

  it('should handle complex combinations', () => {
    expect(cn(
      'base-class',
      ['array-class-1', 'array-class-2'],
      { 'conditional-class': true, 'ignored-class': false },
      null,
      'bg-blue-500',
      'bg-red-500' // should override bg-blue-500
    )).toBe('base-class array-class-1 array-class-2 conditional-class bg-red-500');
  });
});

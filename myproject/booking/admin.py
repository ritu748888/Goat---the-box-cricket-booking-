from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import Venue, Court, Booking, Review, Advertisement, Tournament


# Custom Admin Site Configuration
admin.site.site_header = "GOAT Cricket Booking - Admin Panel"
admin.site.site_title = "GOAT Admin"
admin.site.index_title = "Welcome to GOAT Cricket Management Dashboard"


# Inline Admin Classes
class CourtInline(admin.TabularInline):
    model = Court
    extra = 1
    fields = ('name', 'capacity', 'price_per_hour', 'is_active')


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('user', 'date', 'start_time', 'end_time', 'status')
    readonly_fields = ('user', 'date', 'start_time', 'end_time')
    can_delete = False


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating', 'court_count', 'phone', 'created_at')
    list_filter = ('city', 'created_at', 'rating')
    search_fields = ('name', 'city', 'address', 'email')
    inlines = [CourtInline]
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'city')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email')
        }),
        ('Description & Rating', {
            'fields': ('description', 'rating')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def court_count(self, obj):
        count = obj.courts.count()
        return format_html('<span style="background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px;">{} Courts</span>', count)
    court_count.short_description = 'Courts'


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'capacity', 'price_per_hour', 'status_badge', 'booking_count')
    list_filter = ('venue', 'is_active', 'capacity')
    search_fields = ('name', 'venue__name')
    readonly_fields = ('booking_count_display',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('venue', 'name', 'capacity')
        }),
        ('Pricing', {
            'fields': ('price_per_hour',)
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('booking_count_display',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        color = '#4CAF50' if obj.is_active else '#f44336'
        text = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'
    
    def booking_count_display(self, obj):
        return obj.bookings.count()
    booking_count_display.short_description = 'Total Bookings'
    
    def booking_count(self, obj):
        return obj.bookings.count()
    booking_count.short_description = 'Bookings'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'court_name', 'booking_date', 'time_slot', 'players', 'status_badge', 'total_price')
    list_filter = ('status', 'date', 'court__venue', 'created_at')
    search_fields = ('user__email', 'court__name', 'court__venue__name')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at', 'user', 'total_price_display', 'duration_display')
    actions = ['confirm_booking', 'cancel_booking', 'mark_completed']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Booking Details', {
            'fields': ('court', 'date', 'start_time', 'end_time', 'duration_display', 'number_of_players')
        }),
        ('Payment Information', {
            'fields': ('total_price_display',)
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return format_html(
            '<a href="/admin/user/customuser/{}/change/">{}</a>',
            obj.user.id,
            obj.user.email
        )
    user_email.short_description = 'User Email'
    
    def court_name(self, obj):
        return f"{obj.court.venue.name} - {obj.court.name}"
    court_name.short_description = 'Court'
    
    def booking_date(self, obj):
        return obj.date.strftime('%d %b %Y')
    booking_date.short_description = 'Date'
    
    def time_slot(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"
    time_slot.short_description = 'Time'
    
    def players(self, obj):
        return format_html(
            '<span style="background-color: #2196F3; color: white; padding: 3px 8px; border-radius: 3px;">{} Players</span>',
            obj.number_of_players
        )
    players.short_description = 'Players'
    
    def status_badge(self, obj):
        colors = {
            'confirmed': '#4CAF50',
            'pending': '#FF9800',
            'completed': '#2196F3',
            'cancelled': '#f44336'
        }
        color = colors.get(obj.status, '#9E9E9E')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def total_price_display(self, obj):
        return format_html(
            '<span style="font-size: 1.1em; font-weight: bold; color: #4CAF50;">₹{}</span>',
            obj.total_price
        )
    total_price_display.short_description = 'Total Price'
    
    def duration_display(self, obj):
        from datetime import datetime
        start = datetime.combine(obj.date, obj.start_time)
        end = datetime.combine(obj.date, obj.end_time)
        hours = (end - start).total_seconds() / 3600
        return f"{hours:.1f} hours"
    duration_display.short_description = 'Duration'
    
    def confirm_booking(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} booking(s) confirmed successfully!')
    confirm_booking.short_description = '✅ Confirm selected bookings'
    
    def cancel_booking(self, request, queryset):
        updated = queryset.exclude(status='completed').update(status='cancelled')
        self.message_user(request, f'{updated} booking(s) cancelled successfully!')
    cancel_booking.short_description = '❌ Cancel selected bookings'
    
    def mark_completed(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='completed')
        self.message_user(request, f'{updated} booking(s) marked as completed!')
    mark_completed.short_description = '✔️ Mark as completed'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'venue_name', 'rating_badge', 'created_at')
    list_filter = ('rating', 'created_at', 'venue')
    search_fields = ('user__email', 'venue__name', 'comment')
    readonly_fields = ('created_at', 'user', 'venue')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def venue_name(self, obj):
        return obj.venue.name
    venue_name.short_description = 'Venue'
    
    def rating_badge(self, obj):
        colors = {
            5: '#4CAF50',
            4: '#8BC34A',
            3: '#FF9800',
            2: '#F44336',
            1: '#9C27B0'
        }
        color = colors.get(obj.rating, '#9E9E9E')
        stars = '⭐' * obj.rating
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{} {}/5</span>',
            color, stars, obj.rating
        )
    rating_badge.short_description = 'Rating'


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'contact_person_name', 'promotion_badge', 'status_badge', 'created_at')
    list_filter = ('promotion_type', 'status', 'created_at')
    search_fields = ('brand_name', 'contact_person_name', 'email', 'company_details')
    readonly_fields = ('created_at', 'updated_at', 'submitted_info')
    actions = ['approve_ads', 'reject_ads', 'mark_active']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Brand Information', {
            'fields': ('brand_name', 'company_details')
        }),
        ('Contact Person', {
            'fields': ('contact_person_name', 'email', 'mobile_no')
        }),
        ('Sponsorship Details', {
            'fields': ('promotion_type', 'advertise_duration', 'submitted_info')
        }),
        ('Admin Actions', {
            'fields': ('status',),
            'description': 'Approve or reject sponsorship requests'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def promotion_badge(self, obj):
        colors = {
            'ground': '#2196F3',
            'tournament': '#FF5722',
            'both': '#9C27B0'
        }
        color = colors.get(obj.promotion_type, '#9E9E9E')
        labels = {
            'ground': 'Ground',
            'tournament': 'Tournament',
            'both': 'Both'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color, labels.get(obj.promotion_type, obj.promotion_type)
        )
    promotion_badge.short_description = 'Promotion Type'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FF9800',
            'approved': '#4CAF50',
            'rejected': '#f44336',
            'active': '#2196F3'
        }
        color = colors.get(obj.status, '#9E9E9E')
        icons = {
            'pending': '⏳',
            'approved': '✅',
            'rejected': '❌',
            'active': '🔴'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{} {}</span>',
            color, icons.get(obj.status, ''), obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def submitted_info(self, obj):
        return format_html(
            '<div style="background-color: #f5f5f5; padding: 10px; border-radius: 4px;"><strong>Submitted on:</strong> {}<br><strong>Duration:</strong> {}</div>',
            obj.created_at.strftime('%d %b %Y, %H:%M'),
            obj.advertise_duration
        )
    submitted_info.short_description = 'Submission Details'
    
    def approve_ads(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'{updated} advertisement(s) approved! ✅')
    approve_ads.short_description = '✅ Approve selected advertisements'
    
    def reject_ads(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{updated} advertisement(s) rejected! ❌')
    reject_ads.short_description = '❌ Reject selected advertisements'
    
    def mark_active(self, request, queryset):
        updated = queryset.filter(status='approved').update(status='active')
        self.message_user(request, f'{updated} advertisement(s) marked as active! 🔴')
    mark_active.short_description = '🔴 Mark as active'


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue_name', 'start_date', 'end_date', 'max_teams', 'status_badge', 'entry_fee')
    list_filter = ('status', 'start_date', 'venue')
    search_fields = ('name', 'venue__name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'tournament_summary')
    actions = ['mark_ongoing', 'mark_completed', 'mark_cancelled']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Tournament Information', {
            'fields': ('name', 'description', 'venue')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'start_time')
        }),
        ('Details', {
            'fields': ('max_teams', 'entry_fee', 'prize_pool', 'rules')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_email', 'contact_phone')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Tournament Summary', {
            'fields': ('tournament_summary',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def venue_name(self, obj):
        return f"{obj.venue.name}, {obj.venue.city}"
    venue_name.short_description = 'Venue'
    
    def status_badge(self, obj):
        colors = {
            'upcoming': '#FF9800',
            'ongoing': '#2196F3',
            'completed': '#4CAF50',
            'cancelled': '#f44336'
        }
        color = colors.get(obj.status, '#9E9E9E')
        icons = {
            'upcoming': '📅',
            'ongoing': '🔴',
            'completed': '✅',
            'cancelled': '❌'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{} {}</span>',
            color, icons.get(obj.status, ''), obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def tournament_summary(self, obj):
        days = (obj.end_date - obj.start_date).days + 1
        return format_html(
            '<div style="background-color: #f5f5f5; padding: 10px; border-radius: 4px;">'
            '<strong>📅 Duration:</strong> {} days ({} to {})<br>'
            '<strong>👥 Max Teams:</strong> {}<br>'
            '<strong>💰 Entry Fee:</strong> ₹{}<br>'
            '<strong>🏆 Prize Pool:</strong> {}<br>'
            '<strong>📝 Rules:</strong> {}'
            '</div>',
            days,
            obj.start_date.strftime('%d %b'),
            obj.end_date.strftime('%d %b %Y'),
            obj.max_teams,
            obj.entry_fee if obj.entry_fee > 0 else 'Free',
            obj.prize_pool if obj.prize_pool else 'TBD',
            obj.rules[:100] + '...' if len(obj.rules) > 100 else obj.rules
        )
    tournament_summary.short_description = 'Tournament Summary'
    
    def mark_ongoing(self, request, queryset):
        updated = queryset.filter(status='upcoming').update(status='ongoing')
        self.message_user(request, f'{updated} tournament(s) marked as ongoing! 🔴')
    mark_ongoing.short_description = '🔴 Mark as ongoing'
    
    def mark_completed(self, request, queryset):
        updated = queryset.filter(status='ongoing').update(status='completed')
        self.message_user(request, f'{updated} tournament(s) marked as completed! ✅')
    mark_completed.short_description = '✅ Mark as completed'
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} tournament(s) cancelled! ❌')
    mark_cancelled.short_description = '❌ Cancel tournaments'

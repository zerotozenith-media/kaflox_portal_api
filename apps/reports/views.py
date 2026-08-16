import io
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from apps.projects.models import Project


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def progress_report(request, project_id):
    """Generate PDF progress report for a project."""
    try:
        if request.user.role == 'client':
            project = Project.objects.get(id=project_id, client=request.user)
        else:
            project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        from rest_framework.response import Response
        from rest_framework import status
        return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph('KAFLOX ENGINEERING SERVICES LIMITED', styles['Title']))
    story.append(Paragraph(f'Progress Report: {project.name}', styles['Heading2']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f'Client: {project.client.full_name}', styles['Normal']))
    story.append(Paragraph(f'Project Value: {project.currency} {project.contract_value:,.2f}', styles['Normal']))
    story.append(Paragraph(f'Progress: {project.progress_percent}%', styles['Normal']))
    story.append(Paragraph(f'Stages: {project.completed_stages} of {project.total_stages} complete', styles['Normal']))
    story.append(Spacer(1, 12))

    for stage in project.stages.all().order_by('order'):
        story.append(Paragraph(f'Stage {stage.order}: {stage.name} -- {stage.get_status_display()}', styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="progress_report_{project.id}.pdf"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_report(request, project_id):
    """Generate PDF payment report for a project."""
    try:
        if request.user.role == 'client':
            project = Project.objects.get(id=project_id, client=request.user)
        else:
            project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        from rest_framework.response import Response
        from rest_framework import status
        return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    from apps.payments.models import Payment
    payments = Payment.objects.filter(project=project, status=Payment.CONFIRMED)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph('KAFLOX ENGINEERING SERVICES LIMITED', styles['Title']))
    story.append(Paragraph(f'Payment Report: {project.name}', styles['Heading2']))
    story.append(Spacer(1, 12))

    for pay in payments:
        story.append(Paragraph(
            f'{pay.stage.name if pay.stage else "General"}: {pay.currency} {pay.amount:,.2f} -- {pay.confirmed_at.strftime("%d %b %Y") if pay.confirmed_at else "Pending"}',
            styles['Normal']
        ))

    story.append(Spacer(1, 12))
    story.append(Paragraph(f'Total Paid: {project.currency} {project.total_paid:,.2f}', styles['Heading3']))

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payment_report_{project.id}.pdf"'
    return response
